#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = REPO_ROOT / "snapshot"
REPORTS_ROOT = REPO_ROOT / "reports"
HOME = Path.home()

IGNORE_NAMES = {"__pycache__", "node_modules"}
IGNORE_SUFFIXES = {".pyc", ".pyo", ".lock", ".tmp"}


@dataclass(frozen=True)
class Target:
    src: Path
    dest: str
    kind: str
    required: bool = False


def targets() -> list[Target]:
    return [
        Target(HOME / ".hermes" / "config.yaml", "hermes/config.yaml", "file", True),
        Target(HOME / ".hermes" / ".env", "hermes/.env", "file", True),
        Target(HOME / ".hermes" / "auth.json", "hermes/auth.json", "file", True),
        Target(HOME / ".hermes" / "memories", "hermes/memories", "dir", True),
        Target(HOME / ".hermes" / "skills", "hermes/skills", "dir", True),
        Target(HOME / ".hermes" / "pairing", "hermes/pairing", "dir", False),
        Target(HOME / ".hermes" / "gateway_state.json", "hermes/gateway_state.json", "file", False),
        Target(HOME / ".hermes" / "channel_directory.json", "hermes/channel_directory.json", "file", False),
        Target(HOME / ".hermes" / "profiles", "hermes/profiles", "dir", False),
        Target(HOME / ".hermes" / "cron", "hermes/cron", "dir", False),
        Target(HOME / ".hermes" / "plugins", "hermes/plugins", "dir", False),
        Target(HOME / ".config" / "himalaya" / "config.toml", "config/himalaya/config.toml", "file", False),
        Target(HOME / ".config" / "himalaya" / "gmail-app-password.sh", "config/himalaya/gmail-app-password.sh", "file", False),
        Target(HOME / ".config" / "x-cli" / ".env", "config/x-cli/.env", "file", False),
        Target(Path("/etc/apache2/sites-available/assetloan.my.id.conf"), "system/apache2/sites-available/assetloan.my.id.conf", "file", False),
        Target(HOME / ".gitconfig", "home/.gitconfig", "file", False),
        # Target(HOME / ".git-credentials", "home/.git-credentials", "file", False),  # SKIPPED - contains secrets
        Target(HOME / ".local" / "bin" / "repliz-api", "home/.local/bin/repliz-api", "file", False),
    ]


def should_ignore(path: Path) -> bool:
    if path.name in IGNORE_NAMES:
        return True
    return path.suffix in IGNORE_SUFFIXES


def wipe_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        wipe_path(dest)
    shutil.copy2(src, dest)


def copy_dir(src: Path, dest: Path) -> None:
    if dest.exists() or dest.is_symlink():
        wipe_path(dest)

    def _ignore(_root: str, names: list[str]) -> set[str]:
        skipped = set()
        for name in names:
            p = Path(name)
            if p.name in IGNORE_NAMES or p.suffix in IGNORE_SUFFIXES:
                skipped.add(name)
        return skipped

    shutil.copytree(src, dest, ignore=_ignore, copy_function=shutil.copy2)


def run_command(cmd: list[str], cwd: Path | None = None) -> dict:
    try:
        result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=60)
        return {
            "command": cmd,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as exc:
        return {
            "command": cmd,
            "error": repr(exc),
        }


def collect_inventory() -> dict:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "repo_root": str(REPO_ROOT),
        "commands": {
            "hermes_version": run_command(["hermes", "--version"]),
            "hermes_memory_status": run_command(["hermes", "memory", "status"]),
            "hermes_profile_list": run_command(["hermes", "profile", "list"]),
            "git_version": run_command(["git", "--version"]),
            "repo_git_status": run_command(["git", "status", "--short"], cwd=REPO_ROOT),
            "repo_git_remote": run_command(["git", "remote", "-v"], cwd=REPO_ROOT),
        },
    }


def path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    if path.is_dir():
        total = 0
        for sub in path.rglob("*"):
            if sub.is_file() and not should_ignore(sub):
                total += sub.stat().st_size
        return total
    return 0


def sync() -> dict:
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    missing_required: list[str] = []

    for target in targets():
        dest_path = SNAPSHOT_ROOT / target.dest
        src_exists = target.src.exists()
        entry = {
            "src": str(target.src),
            "dest": str(dest_path),
            "kind": target.kind,
            "required": target.required,
            "exists": src_exists,
        }

        if not src_exists:
            if dest_path.exists() or dest_path.is_symlink():
                wipe_path(dest_path)
            if target.required:
                missing_required.append(str(target.src))
            manifest.append(entry)
            continue

        if target.kind == "file":
            copy_file(target.src, dest_path)
        elif target.kind == "dir":
            copy_dir(target.src, dest_path)
        else:
            raise ValueError(f"Unknown target kind: {target.kind}")

        entry["size_bytes"] = path_size(dest_path)
        manifest.append(entry)

    inventory = collect_inventory()
    (REPORTS_ROOT / "snapshot_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (REPORTS_ROOT / "system_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")

    summary_lines = [
        f"timestamp_utc: {inventory['timestamp_utc']}",
        f"repo_root: {REPO_ROOT}",
        f"snapshot_root: {SNAPSHOT_ROOT}",
        f"targets_total: {len(manifest)}",
        f"targets_present: {sum(1 for item in manifest if item['exists'])}",
        f"missing_required: {len(missing_required)}",
    ]
    if missing_required:
        summary_lines.append("missing_required_paths:")
        summary_lines.extend(f"- {item}" for item in missing_required)
    (REPORTS_ROOT / "summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    result = {
        "snapshot_root": str(SNAPSHOT_ROOT),
        "reports_root": str(REPORTS_ROOT),
        "targets_total": len(manifest),
        "targets_present": sum(1 for item in manifest if item['exists']),
        "missing_required": missing_required,
    }
    return result


if __name__ == "__main__":
    result = sync()
    print(json.dumps(result, indent=2))
    if result["missing_required"]:
        raise SystemExit(1)
