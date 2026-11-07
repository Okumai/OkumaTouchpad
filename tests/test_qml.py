"""Opt-in real Quickshell smoke test: no input settings are applied.

Run in an Omarchy session: OKUMA_QML_SMOKE=1 python3 -m unittest discover -s tests -v
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(os.environ.get("OKUMA_QML_SMOKE") == "1" and shutil.which("qs"),
                     "Set OKUMA_QML_SMOKE=1 inside an Omarchy session")
class QmlSmokeTests(unittest.TestCase):
    def test_real_helper_paths_and_enable_time_launcher_registration(self):
        source = Path(__file__).resolve().parents[1]
        shell = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy")) / "shell"
        with tempfile.TemporaryDirectory(prefix="okuma-qml-") as directory:
            root = Path(directory)
            for name in ("Commons", "Ui", "services"):
                (root / name).symlink_to(shell / name, target_is_directory=True)
            for name in ("Touchpad.qml", "touchpad.py", "launcher.py", "okuma-touchpad.desktop"):
                shutil.copy2(source / name, root / name)
            for name in ("i18n", "icons"):
                shutil.copytree(source / name, root / name)
            (root / "shell.qml").write_text('''import QtQuick
import Quickshell
ShellRoot {
    Touchpad { id: panel }
    Timer { interval: 500; running: true; onTriggered: panel.execute("describe") }
    Timer {
        interval: 4000; running: true
        onTriggered: { console.log("OKUMA_SMOKE " + panel.diagnostics()); Qt.quit(); }
    }
}
''')
            result = subprocess.run(["qs", "-p", str(root), "--no-color"], capture_output=True,
                                    text=True, timeout=15,
                                    env=os.environ | {"XDG_DATA_HOME": str(root / "data"),
                                                      "QML_DISABLE_DISK_CACHE": "1"})
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            marker = next((line.split("OKUMA_SMOKE ", 1)[1] for line in output.splitlines()
                           if "OKUMA_SMOKE " in line), None)
            self.assertIsNotNone(marker, output)
            state = json.loads(marker)
            self.assertEqual(state["fieldCount"], 23, output)
            self.assertNotEqual(state["resultState"], "failed", output)
            self.assertEqual(state["launcherMessage"], "", output)
            self.assertTrue((root / "data/applications/okuma-touchpad.desktop").is_file())
            self.assertTrue((root / "data/icons/hicolor/scalable/apps/okuma-touchpad.svg").is_file())
