#!/usr/bin/env python3
"""Install or remove the user-owned freedesktop application launcher."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
from touchpad import atomic_write

DESKTOP_ID = "okuma-touchpad.desktop"
MARKER = "X-OkumaTouchpad-Managed=true"
ROOT = Path(__file__).resolve().parent


def data_home():
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")


def safe_path(path):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError(f"Refusing symlink launcher path: {path}")


def install(home=None):
    home = home or data_home()
    desktop = home / "applications" / DESKTOP_ID
    icon = home / "icons/hicolor/scalable/apps/okuma-touchpad.svg"
    for path in (desktop, icon):
        safe_path(path)
    if desktop.exists() and MARKER not in desktop.read_text().splitlines():
        raise ValueError(f"Refusing to overwrite an unowned desktop entry: {desktop}")
    source_icon = (ROOT / "icons/okuma-touchpad.svg").read_text()
    if icon.exists() and icon.read_text() != source_icon:
        raise ValueError(f"Refusing to overwrite a different icon: {icon}")
    desktop.parent.mkdir(parents=True, exist_ok=True)
    icon.parent.mkdir(parents=True, exist_ok=True)
    source_desktop = (ROOT / DESKTOP_ID).read_text()
    changed = False
    for path, text in ((icon, source_icon), (desktop, source_desktop)):
        if not path.exists() or path.read_text() != text:
            atomic_write(path, text)
            changed = True
    if changed and shutil.which("update-desktop-database"):
        subprocess.run(["update-desktop-database", str(desktop.parent)], check=True, timeout=15)
    print(f"Application launcher installed: {desktop}")


def remove(home=None):
    home = home or data_home()
    desktop = home / "applications" / DESKTOP_ID
    icon = home / "icons/hicolor/scalable/apps/okuma-touchpad.svg"
    for path in (desktop, icon):
        safe_path(path)
    if desktop.exists():
        if MARKER not in desktop.read_text().splitlines():
            raise ValueError("Refusing to remove an unowned desktop entry")
        desktop.unlink()
    if icon.exists() and icon.read_text() == (ROOT / "icons/okuma-touchpad.svg").read_text():
        icon.unlink()
    if desktop.parent.exists() and shutil.which("update-desktop-database"):
        subprocess.run(["update-desktop-database", str(desktop.parent)], check=True, timeout=15)
    print("Owned application launcher removed; gesture configuration was not changed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "remove"])
    args = parser.parse_args()
    try:
        (install if args.action == "install" else remove)()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f"OkumaTouchpad launcher: {error}\n")
