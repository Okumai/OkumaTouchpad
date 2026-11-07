"""Application launcher installation must be repeatable and user-owned."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import launcher


class LauncherTests(unittest.TestCase):
    def test_install_repeat_remove(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(launcher.shutil, "which", return_value=None):
            home = Path(directory)
            launcher.install(home)
            launcher.install(home)
            desktop = home / "applications" / launcher.DESKTOP_ID
            text = desktop.read_text()
            self.assertIn("Exec=omarchy-shell shell summon okuma.dev_touchpad4omarchy {}", text)
            self.assertIn("Terminal=false", text)
            self.assertTrue((home / "icons/hicolor/scalable/apps/okuma-touchpad.svg").exists())
            launcher.remove(home)
            launcher.remove(home)
            self.assertFalse(desktop.exists())

    def test_unchanged_registration_does_not_rewrite_or_refresh_cache(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(launcher.shutil, "which", return_value=None):
            home = Path(directory)
            launcher.install(home)
            desktop = home / "applications" / launcher.DESKTOP_ID
            before = desktop.stat().st_mtime_ns
            with patch.object(launcher.shutil, "which", return_value="/usr/bin/update-desktop-database"), patch.object(launcher.subprocess, "run") as run:
                launcher.install(home)
                run.assert_not_called()
            self.assertEqual(desktop.stat().st_mtime_ns, before)

    def test_plugin_registers_launcher_without_applying_settings(self):
        qml = (Path(launcher.__file__).parent / "Touchpad.qml").read_text()
        self.assertIn("Component.onCompleted: launcherWorker.running = true", qml)
        self.assertIn('root.localFile("launcher.py"), "install"', qml)
        self.assertIn('localFile("touchpad.py"), action', qml)
        self.assertNotIn('directory + "touchpad.py"', qml)
        self.assertNotIn('Component.onCompleted: execute("apply")', qml)

    def test_unowned_entry_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            desktop = home / "applications" / launcher.DESKTOP_ID
            desktop.parent.mkdir()
            desktop.write_text("[Desktop Entry]\nName=Personal\n")
            with self.assertRaises(ValueError):
                launcher.install(home)
            with self.assertRaises(ValueError):
                launcher.remove(home)

    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / "applications").symlink_to(home, target_is_directory=True)
            with self.assertRaises(ValueError):
                launcher.install(home)

    def test_xdg_data_home(self):
        with patch.dict(os.environ, {"XDG_DATA_HOME": "/tmp/okuma-test-data"}):
            self.assertEqual(launcher.data_home(), Path("/tmp/okuma-test-data"))
