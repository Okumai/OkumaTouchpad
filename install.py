#!/usr/bin/env python3
"""Install the settings panel. Never apply or migrate gestures implicitly."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import launcher

ROOT = Path(__file__).resolve().parent
PLUGIN_ID = "okuma.dev_touchpad4omarchy"


def run(*args):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, text=True, timeout=30).stdout.strip()


def wait_for(check, message):
    for _ in range(40):
        try:
            if check():
                return
        except (subprocess.SubprocessError, ValueError, TypeError, AttributeError):
            pass
        time.sleep(0.25)
    raise RuntimeError(message)


def install_snapshot(target, update=False):
    """Explicitly update local snapshots; never overwrite a git-managed checkout."""
    if target.exists():
        if json.loads((target / "manifest.json").read_text()).get("id") != PLUGIN_ID:
            raise RuntimeError("Unexpected plugin identity at installation target")
        if ROOT == target.resolve():
            return
        if not update:
            print("Existing source retained. Use --update for local snapshots, or omarchy plugin update "
                  + PLUGIN_ID + " for git installations.")
            return
        if (target / ".git").exists():
            raise RuntimeError("Git-managed plugin: update with omarchy plugin update " + PLUGIN_ID)
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".okuma-touchpad-stage-", dir=target.parent))
    backup = None
    try:
        shutil.copytree(ROOT, stage, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.bak*", ".pytest_cache"))
        run("omarchy", "plugin", "validate", stage)
        if target.exists():
            backup = target.parent.parent / "plugin-backups" / (PLUGIN_ID + "-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
            if any(p.is_symlink() for p in (backup, *backup.parents)):
                raise RuntimeError("Refusing a symlink backup path")
            backup.parent.mkdir(parents=True, exist_ok=True)
            target.rename(backup)
        try:
            stage.rename(target)
        except OSError:
            if backup is not None:
                backup.rename(target)
            raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    if backup is not None:
        print(f"Previous snapshot retained: {backup}")
    print("Installed a local snapshot (not a git-managed checkout).")


def install(yes=False, update=False):
    for executable in ("omarchy", "omarchy-shell", "hyprctl"):
        if not shutil.which(executable):
            raise RuntimeError(f"Required command not found: {executable}")
    home = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    target = home / "omarchy/plugins" / PLUGIN_ID
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise RuntimeError("Refusing a symlink installation path")
    run("omarchy", "plugin", "validate", ROOT)
    print(f"Install settings panel: {target}")
    print("Plugins run unsandboxed. No input preferences or gestures will be changed.")
    if not yes and input("Continue? [y/N] ").strip().lower() not in {"y", "yes"}:
        raise RuntimeError("Installation cancelled")
    install_snapshot(target, update)
    run("omarchy", "plugin", "validate", target)
    try:
        run("omarchy-shell", "shell", "rescanPlugins")
    except subprocess.SubprocessError:
        pass
    wait_for(lambda: any(p.get("id") == PLUGIN_ID for p in json.loads(run("omarchy", "plugin", "list", "--json"))),
             "Plugin discovery did not complete; inspect shell logs")
    try:
        run("omarchy", "plugin", "enable", PLUGIN_ID)
    except subprocess.SubprocessError:
        # An IPC interruption is acceptable only if the live plugin subsequently responds.
        pass
    wait_for(lambda: run("omarchy-shell", "shell", "call", PLUGIN_ID, "status", "") in {"open", "closed"},
             "Settings panel failed to load; inspect shell logs")
    launcher.install()
    try:
        diagnostics = json.loads(run("omarchy-shell", "shell", "call", PLUGIN_ID, "diagnostics", ""))
        if "resultState" not in diagnostics:
            print("Warning: the shell is still running an older cached panel. "
                  "Run omarchy restart shell deliberately to load the updated code.")
    except (ValueError, TypeError, subprocess.SubprocessError):
        print("Warning: could not verify the running panel revision. "
              "If the panel is stale, deliberately run omarchy restart shell.")
    print("Settings panel enabled. Find OkumaTouchpad in your application launcher.")
    print("No global gestures were changed.")
    print(f"Open: omarchy-shell shell summon {PLUGIN_ID} '{{}}'")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--update", action="store_true", help="Replace a local snapshot, retaining a backup; refuses git checkouts")
    args = parser.parse_args()
    try:
        install(args.yes, args.update)
    except (OSError, ValueError, RuntimeError, EOFError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Installation failed: {error}\nCompleted steps are retained; no gesture migration was attempted.\n")


if __name__ == "__main__":
    main()
