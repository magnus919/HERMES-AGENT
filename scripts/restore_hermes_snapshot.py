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
    errors = []
    for target in targets():
        src = SNAPSHOT_ROOT / target.src
        if not src.exists():
            skipped.append(str(src))
            continue
        # Skip system paths that require root (e.g. /etc/apache2)
        if str(target.dest).startswith("/etc/") or str(target.dest).startswith("/var/"):
            skipped.append(f"{src} (system path, requires root)")
            continue
        try:
            if target.kind == "file":
                copy_file(src, target.dest)
            elif target.kind == "dir":
                copy_dir(src, target.dest)
            else:
                raise ValueError(f"Unknown target kind: {target.kind}")
            restored.append({"src": str(src), "dest": str(target.dest), "kind": target.kind})
        except PermissionError as e:
            errors.append(f"Permission denied: {target.dest} — {e}")
            skipped.append(f"{src} (permission denied)")
        except Exception as e:
            errors.append(f"Error restoring {target.dest}: {e}")
            skipped.append(f"{src} ({e})")

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

    # Install/upgrade ClawTeam from GitHub
    clawteam_install = {"attempted": False, "installed": False, "version": None}
    clawteam_install["attempted"] = True
    clawteam_venv = HOME / "clawteam-venv"
    clawteam_bin = clawteam_venv / "bin"

    # Check if already installed
    existing_version = None
    if clawteam_bin.exists():
        result = subprocess.run(
            [str(clawteam_bin / "clawteam"), "--version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            existing_version = result.stdout.strip()

    # Create venv and install latest from GitHub
    import sys
    if not clawteam_venv.exists():
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(clawteam_venv)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            clawteam_install["status"] = "venv_create_failed"
            clawteam_install["stderr"] = result.stderr.strip().splitlines()[-3:]
        else:
            clawteam_install["status"] = "venv_created"

    if clawteam_venv.exists():
        result = subprocess.run(
            [str(clawteam_bin / "pip"), "install", "-e",
             "git+https://github.com/HKUDS/ClawTeam.git#egg=clawteam"],
            capture_output=True, text=True
        )
        clawteam_install["installed"] = result.returncode == 0
        if result.returncode == 0:
            clawteam_install["status"] = "installed"
            # Get new version
            result = subprocess.run(
                [str(clawteam_bin / "clawteam"), "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                clawteam_install["version"] = result.stdout.strip()
        else:
            clawteam_install["status"] = "install_failed"
            clawteam_install["stderr"] = result.stderr.strip().splitlines()[-3:]

        # Create symlinks in /usr/local/bin
        for name in ["clawteam", "oh"]:
            symlink = Path("/usr/local/bin") / name
            target = clawteam_bin / name
            if symlink.exists() or symlink.is_symlink():
                symlink.unlink()
            if target.exists():
                symlink.symlink_to(target)

    return {
        "repo_root": str(REPO_ROOT),
        "restored_count": len(restored),
        "skipped_missing_snapshot_entries": skipped,
        "errors": errors,
        "x_cli_install": x_cli_install,
        "clawteam_install": clawteam_install,
    }


if __name__ == "__main__":
    result = restore()
    print(json.dumps(result, indent=2))
