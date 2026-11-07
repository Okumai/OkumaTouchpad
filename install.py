#!/usr/bin/env python3
"""Install the settings panel. Never apply or migrate gestures implicitly."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
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


def install(yes=False):
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
    if target.exists():
        if json.loads((target / "manifest.json").read_text()).get("id") != PLUGIN_ID:
            raise RuntimeError("Unexpected plugin identity at installation target")
        run("omarchy", "plugin", "validate", target)
        print("Reusing installed plugin; update its source separately.")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.bak*"))
        print("Installed a local snapshot (not a git-managed checkout).")
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
    print("Settings panel enabled. Find OkumaTouchpad in your application launcher.")
    print("No global gestures were changed.")
    print(f"Open: omarchy-shell shell summon {PLUGIN_ID} '{{}}'")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    try:
        install(args.yes)
    except (OSError, ValueError, RuntimeError, EOFError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Installation failed: {error}\nCompleted steps are retained; no gesture migration was attempted.\n")


if __name__ == "__main__":
    main()
