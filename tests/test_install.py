"""Snapshot updates are explicit, backed up and never replace git checkouts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import install as installer


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        home = Path(self.temp.name)
        self.source = home / "source"
        self.source.mkdir()
        (self.source / "manifest.json").write_text(json.dumps({"id": installer.PLUGIN_ID}))
        (self.source / "panel.qml").write_text("new version")
        self.target = home / "omarchy/plugins" / installer.PLUGIN_ID

    def install(self, update=False):
        with patch.object(installer, "ROOT", self.source), patch.object(installer, "run", return_value="ok"):
            installer.install_snapshot(self.target, update)

    def test_install_and_explicit_update_retains_backup(self):
        self.install()
        (self.target / "panel.qml").write_text("local version")
        self.install()
        self.assertEqual((self.target / "panel.qml").read_text(), "local version")
        self.install(update=True)
        self.assertEqual((self.target / "panel.qml").read_text(), "new version")
        backups = list((self.target.parent.parent / "plugin-backups").glob("*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "panel.qml").read_text(), "local version")

    def test_git_checkout_is_never_overwritten(self):
        self.install()
        (self.target / ".git").mkdir()
        with self.assertRaisesRegex(RuntimeError, "Git-managed"):
            self.install(update=True)

    def test_failed_validation_retains_existing_snapshot(self):
        self.install()
        (self.target / "panel.qml").write_text("local version")
        with patch.object(installer, "ROOT", self.source), patch.object(installer, "run", side_effect=RuntimeError("invalid")):
            with self.assertRaises(RuntimeError):
                installer.install_snapshot(self.target, True)
        self.assertEqual((self.target / "panel.qml").read_text(), "local version")
        self.assertEqual(list(self.target.parent.glob(".okuma-touchpad-stage-*")), [])


if __name__ == "__main__":
    unittest.main()
