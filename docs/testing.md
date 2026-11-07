# Testing

## Portable checks

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
omarchy plugin validate .
/usr/lib/qt6/bin/qmllint -I /usr/share/omarchy/shell Touchpad.qml
python3 touchpad.py preview > /tmp/okuma-touchpad-preview.lua
luac -p /tmp/okuma-touchpad-preview.lua
```

Tests exercise input validation, generated Lua callbacks, single-fire behavior,
configuration ownership, comment/string-aware conflict scanning, idempotent loading
and removal, symlink rejection, missing dependencies and rollback. Temporary
configuration roots and mocks prevent changes to the live desktop.

## Desktop acceptance checklist (required before release)

- Record Omarchy, Quickshell, Hyprland, touchpad model and driver versions.
- Install in a disposable user session; verify discovery, enable and `status` IPC.
- Open/close/reopen the panel, including after plugin hot reload.
- Test keyboard Tab/Space/Enter, Escape, scrolling, small screens and multiple monitors.
- Verify every switch, enum, numeric field and plugin ID editor changes the intended
  draft; malformed values must fail before any saved or generated file changes.
- Confirm Reload saved discards drafts, Preview does not write, and Apply is explicit.
- Test large diagnostic output and markup-shaped untrusted output: it must remain
  literal plain text and must not trigger resource loading.
- Change theme and language while open; English is the shipped fallback. Confirm
  right-to-left layout does not break controls.
- Test natural and traditional two-finger scrolling in multiple applications; test
  the independent workspace inversion setting. Test mouse wheels remain unchanged.
- Test tap click, tap button mapping, physical clickfinger behavior, typing
  suppression, three-finger drag and the global scroll multiplier.
- Test workspace swipe continuity, cancellation, distance and empty neighbors.
- Test vertical actions, primary inward/outward pinch, extra three-finger spread,
  disabled actions, all action choices and per-gesture finger counts.
- Test pinch thresholds and once-per-gesture behavior on supported hardware.
- Test missing Launchpad, conflicting registrations and overridden effective values.
- Test migration from Launchpad and manual bindings using backups.
- Test apply, reapply, remove, repeated remove, rollback and manual restoration.
- Confirm disabling the panel leaves native bindings until explicit removal; document
  this distinction in release notes and user support.

No unit test, manifest validator or QML linter can prove physical gesture support.
Do not claim cross-device compatibility until actual hardware has been tested.
