"""Portable validation, generation, ownership and rollback regression tests."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import touchpad as t


class SettingsTests(unittest.TestCase):
    def test_defaults_and_schema(self):
        self.assertEqual(len(t.DEFAULTS), len(t.FIELDS))
        self.assertEqual(t.validate({}), t.DEFAULTS)
        catalog = json.loads((Path(t.__file__).parent / "i18n/en.json").read_text())
        for f in t.FIELDS:
            self.assertIn("setting." + f["key"], catalog)
            self.assertIn("group." + f["group"], catalog)

    def test_invalid_values(self):
        for data in ({"unknown": True}, {"naturalScroll": 1}, {"pinchThreshold": float("nan")},
                     {"scrollFactor": float("inf")}, {"workspaceDistance": 50.5},
                     {"workspaceFingers": True}, {"launchpadPlugin": "x; touch /tmp/unsafe"},
                     {"launchpadPlugin": "x..y"}, {"swipeUp": "execute-arbitrary-command"}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                t.validate(data)

    def test_customizations(self):
        source, digest = t.render({"naturalScroll": False, "workspaceInvert": True, "swipeUp": "none"})
        self.assertIn("natural_scroll = false", source)
        self.assertIn("workspace_swipe_invert = true", source)
        self.assertNotIn('direction = "up"', source)
        self.assertIn(digest, source)
        self.assertEqual(t.render({})[1], t.render(t.DEFAULTS)[1])

    def test_three_finger_profile_owns_one_pinch(self):
        source, _ = t.render({"pinchFingers": 3})
        self.assertEqual(source.count('direction = "pinch"'), 1)
        self.assertIn("ignored", " ".join(t.warnings(t.validate({"pinchFingers": 3}))))

    def test_disabled_gestures(self):
        source, _ = t.render(dict(workspaceSwipe=False, swipeUp="none", swipeDown="none",
                                  pinchIn="none", pinchOut="none", threeFingerSpread="none"))
        self.assertNotIn("hl.gesture", source)

    @unittest.skipUnless(shutil.which("lua"), "Lua is required")
    def test_generated_callbacks(self):
        source, _ = t.render({})
        harness = '''local commands, bindings = {}, {}
hl = {
  config = function(c) assert(c.input.touchpad.natural_scroll == true) end,
  gesture = function(g) bindings[g.fingers .. g.direction] = g.action end,
  exec_cmd = function(c) table.insert(commands, c) end,
}
'''
        checks = '''
local p = bindings["4pinch"]
p.start({scale=1}); p.update({scale=0.89}); p.update({scale=0.8})
assert(#commands == 1 and commands[1]:find("summon", 1, true))
p.finish({}); p.start({scale=1.11}); assert(#commands == 2)
assert(commands[2]:find("hide", 1, true))
local spread = bindings["3pinch"]
spread.start({scale=0.8}); assert(#commands == 2)
spread.update({scale=1.11}); spread.update({scale=1.2}); assert(#commands == 3)
bindings["4up"](); assert(commands[4] == "omarchy toggle bar on")
assert(bindings["4horizontal"] == "workspace")
'''
        subprocess.run(["lua", "-"], input=harness + source + checks, text=True, check=True, capture_output=True)


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.main, self.target, self.config = t.paths(self.home)
        self.main.parent.mkdir(parents=True)
        self.main.write_text('-- Personal entry point\nrequire("hypr.input")\n')

    def test_loader_is_idempotent_and_removable(self):
        original = self.main.read_text()
        configured = t.add_loader(original, self.target)
        self.assertEqual(configured, t.add_loader(configured, self.target))
        self.assertEqual(t.remove_loader(configured), original)
        for text in (t.BEGIN, t.END + "\n" + t.BEGIN):
            with self.assertRaises(ValueError):
                t.remove_loader(text)

    def test_comments_and_strings_do_not_conflict(self):
        path = self.main.parent / "input.lua"
        path.write_text('''-- hl.gesture({})
local a = "hl.gesture({})"
local b = [=[hl.gesture({})]=]
--[=[ hl.gesture({}) ]=]
''')
        self.assertEqual(t.conflicts(self.main.parent, self.target), [])
        path.write_text('hl . gesture ( { fingers = 4 } )')
        self.assertEqual(t.conflicts(self.main.parent, self.target), [str(path)])

    def test_conflict_prevents_writes(self):
        original = self.main.read_text()
        (self.main.parent / "input.lua").write_text("hl.gesture({})")
        with patch.object(t, "preflight") as preflight, self.assertRaises(ValueError):
            t.apply(self.home, t.validate({}))
        preflight.assert_not_called()
        self.assertEqual(self.main.read_text(), original)
        self.assertFalse(self.target.exists())

    def test_failed_verification_rolls_back(self):
        original = self.main.read_text()
        with patch.object(t, "run", return_value=""):
            with self.assertRaises(RuntimeError):
                t.transact({self.main: "changed", self.target: "generated"},
                           lambda: (_ for _ in ()).throw(RuntimeError("failure")))
        self.assertEqual(self.main.read_text(), original)
        self.assertFalse(self.target.exists())
        self.assertTrue(list(self.main.parent.glob("*.bak.okuma-touchpad.*")))

    def test_apply_reapply_remove_and_saved_settings(self):
        settings = t.validate({"naturalScroll": False})
        def fake_run(*args):
            if args[:3] == ("hyprctl", "-j", "getoption"):
                option = args[3]
                values = {
                    "natural_scroll": ("bool", False), "tap_to_click": ("bool", True),
                    "tap_button_map": ("str", "lrm"), "clickfinger_behavior": ("bool", True),
                    "disable_while_typing": ("bool", True), "drag_3fg": ("int", 1),
                    "scroll_factor": ("float", 1.0), "workspace_swipe_invert": ("bool", False),
                    "workspace_swipe_distance": ("int", 300), "workspace_swipe_cancel_ratio": ("float", 0.5),
                    "workspace_swipe_use_r": ("bool", True), "workspace_swipe_create_new": ("bool", True),
                }
                kind, value = values[option.split(":")[-1]]
                return json.dumps({kind: value})
            return ""
        with patch.object(t, "preflight"), patch.object(t, "run", side_effect=fake_run):
            t.apply(self.home, settings)
            first = self.main.read_text()
            t.apply(self.home, settings)
            self.assertEqual(first, self.main.read_text())
            self.assertEqual(t.read_settings(self.config), settings)
            t.uninstall(self.home)
            t.uninstall(self.home)
        self.assertFalse(self.target.exists())
        self.assertNotIn(t.BEGIN, self.main.read_text())
        self.assertTrue(self.config.exists())

    def test_symlink_and_unowned_target_refused(self):
        self.target.write_text("-- User file\n")
        with self.assertRaises(ValueError):
            t.apply(self.home, t.validate({}))
        self.target.unlink()
        self.target.symlink_to(self.main)
        with self.assertRaises(ValueError):
            t.atomic_write(self.target, "bad")

    def test_missing_launchpad_does_not_fall_back_silently(self):
        with patch.object(t.shutil, "which", return_value="/usr/bin/tool"), patch.object(t, "run", side_effect=["", "ok", "unavailable"]):
            with self.assertRaisesRegex(RuntimeError, "Launchpad"):
                t.preflight(t.validate({}))


if __name__ == "__main__":
    unittest.main()
