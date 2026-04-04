#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = REPO_ROOT / "snapshot"
HOME = Path.home()


@dataclass(frozen=True)
class Target:
    src: str
    dest: Path
    kind: str


def targets() -> list[Target]:
    return [
        Target("hermes/config.yaml", HOME / ".hermes" / "config.yaml", "file"),
        Target("hermes/.env", HOME / ".hermes" / ".env", "file"),
        Target("hermes/auth.json", HOME / ".hermes" / "auth.json", "file"),
        Target("hermes/memories", HOME / ".hermes" / "memories", "dir"),
        Target("hermes/skills", HOME / ".hermes" / "skills", "dir"),
        Target("hermes/pairing", HOME / ".hermes" / "pairing", "dir"),
        Target("hermes/gateway_state.json", HOME / ".hermes" / "gateway_state.json", "file"),
        Target("hermes/channel_directory.json", HOME / ".hermes" / "channel_directory.json", "file"),
        Target("hermes/profiles", HOME / ".hermes" / "profiles", "dir"),
        Target("hermes/cron", HOME / ".hermes" / "cron", "dir"),
        Target("hermes/plugins", HOME / ".hermes" / "plugins", "dir"),
        Target("config/himalaya/config.toml", HOME / ".config" / "himalaya" / "config.toml", "file"),
        Target("config/himalaya/gmail-app-password.sh", HOME / ".config" / "himalaya" / "gmail-app-password.sh", "file"),
        Target("config/x-cli/.env", HOME / ".config" / "x-cli" / ".env", "file"),
        Target("system/apache2/sites-available/assetloan.my.id.conf", Path("/etc/apache2/sites-available/assetloan.my.id.conf"), "file"),
        Target("home/.gitconfig", HOME / ".gitconfig", "file"),
        Target("home/.git-credentials", HOME / ".git-credentials", "file"),
        Target("home/.local/bin/repliz-api", HOME / ".local" / "bin" / "repliz-api", "file"),
    ]


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
    shutil.copytree(src, dest, copy_function=shutil.copy2)


def restore() -> dict:
    restored = []
    skipped = []
    for target in targets():
        src = SNAPSHOT_ROOT / target.src
        if not src.exists():
            skipped.append(str(src))
            continue
        if target.kind == "file":
            copy_file(src, target.dest)
        elif target.kind == "dir":
            copy_dir(src, target.dest)
        else:
            raise ValueError(f"Unknown target kind: {target.kind}")
        restored.append({"src": str(src), "dest": str(target.dest), "kind": target.kind})

    for path in [HOME / ".hermes" / ".env", HOME / ".hermes" / "auth.json", HOME / ".git-credentials"]:
        if path.exists():
            path.chmod(0o600)
    script_path = HOME / ".config" / "himalaya" / "gmail-app-password.sh"
    if script_path.exists():
        script_path.chmod(0o700)
    x_cli_env = HOME / ".config" / "x-cli" / ".env"
    if x_cli_env.exists():
        x_cli_env.chmod(0o600)
    repliz = HOME / ".local" / "bin" / "repliz-api"
    if repliz.exists():
        repliz.chmod(0o755)

    x_cli_install = {"attempted": False, "installed": False}
    if x_cli_env.exists():
        x_cli_install["attempted"] = True
        if shutil.which("x-cli"):
            x_cli_install["installed"] = True
            x_cli_install["status"] = "already_present"
        elif shutil.which("uv"):
            result = subprocess.run(
                ["uv", "tool", "install", "git+https://github.com/Infatoshi/x-cli.git"],
                capture_output=True,
                text=True,
            )
            x_cli_install["installed"] = result.returncode == 0
            x_cli_install["status"] = "installed" if result.returncode == 0 else "install_failed"
            x_cli_install["exit_code"] = result.returncode
            if result.stdout.strip():
                x_cli_install["stdout"] = result.stdout.strip().splitlines()[-5:]
            if result.stderr.strip():
                x_cli_install["stderr"] = result.stderr.strip().splitlines()[-5:]
        else:
            x_cli_install["status"] = "uv_missing"

    return {
        "repo_root": str(REPO_ROOT),
        "restored_count": len(restored),
        "skipped_missing_snapshot_entries": skipped,
        "x_cli_install": x_cli_install,
    }


if __name__ == "__main__":
    result = restore()
    print(json.dumps(result, indent=2))
