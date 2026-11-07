# Validation status

## Version 0.1.1 portability fixes

Confirmed and fixed:

- Omarchy's git plugin installer never executes this project's `install.py`.
  The keep-loaded panel now registers only its desktop entry/icon on load.
- In a fresh Quickshell config, `Qt.resolvedUrl(".")` returned a directory without
  a trailing slash. Concatenation produced a nonexistent helper path. Both helpers
  now resolve their complete filenames directly. A real opt-in QML regression test
  exercises this path rather than relying solely on text matching.
- Missing optional Launchpad no longer aborts all input changes. New pinch/spread
  defaults are `none`; explicit existing profiles retain their actions with warnings.
- UI distinguishes applied, unapplied, dirty and failed states. Reading preferences
  checks the live loader digest and effective global options.
- Explicit local snapshot updates validate before replacement and retain a backup;
  git checkouts are not overwritten.

Validation for this revision:

- 26 portable unit tests passed; opt-in real QML smoke test passed separately.
- Python compilation, manifest validation, generated Lua parsing and desktop-file
  validation passed. Standalone QML lint exits zero with unresolved import warnings;
  it is not a clean semantic lint.
- Isolated real Quickshell process registered the desktop entry/icon in a temporary
  XDG data directory and populated all 23 settings without applying input changes.
- Isolated QML reapplied the complete existing saved profile successfully. An invalid
  draft then failed before writes, retained dirty state and showed a failure message.
  Hashes of the user's entry point, generated Lua and preferences were unchanged.
  `hyprctl reload` and `hyprctl configerrors` completed without configuration errors.
- Existing shell process retained old QML after snapshot replacement and disable/
  enable. The isolated process loaded the new version. A deliberate shell restart
  may be necessary after updating; no full shell restart was forced in this check.
- No remote-device or physical gesture acceptance is claimed. Per-device overrides
  and driver recognition still require checking on the affected machine.

## Original 0.1.0 automated checks (historical)

- 17 portable unit tests passed, including generated callbacks executed by Lua
  and launcher ownership, symlink, repeat-install and removal tests.
- Python compile checks passed.
- `omarchy plugin validate .` passed.
- Generated default Lua passed `luac -p`.
- Standalone QML lint exits zero but reports unresolved `qs.Commons` imports and
  Quickshell type warnings. This is not a clean semantic lint result.

## Live development desktop checks

Tested on Hyprland 0.56.2 with the installed Omarchy Quickshell shell and a bcm5974
pointer device. This records software checks, not physical gesture recognition.

Completed:

- Installed and enabled the panel through the project installer.
- Summoned the real QML panel and verified open / hide / reopen through shell IPC.
- Read-only `diagnostics` IPC confirmed all 23 settings were populated, the helper
  finished successfully, and the saved profile was read after reopening.
- Migrated existing vertical gestures and Launchpad-managed pinch/workspace blocks
  after timestamped backups. Retained personal preferences and the Launchpad layer
  animation rule outside this project's ownership.
- Preserved measured scroll multiplier 0.4 and workspace inversion enabled, rather
  than replacing them with the initial portable profile defaults.
- Applied and reapplied the saved profile successfully with live digest checks,
  effective-setting verification and no Hyprland configuration errors.
- Removed native configuration and applied it again successfully. Final state is
  installed and active, with the measured preferences preserved.
- Doctor confirmed no remaining literal user gesture conflicts and a matching live
  configuration digest.

Observed limitation:

- After editing installed QML, the current shell retained the old plugin method
  set despite rescan/hot-reload messages. A single `omarchy restart shell` made the
  updated panel available. The installer does not force a shell restart; users
  encountering stale plugin code should close work-sensitive overlays and restart
  the shell deliberately. The exact upstream reload cause has not been established.

## Application launcher and centered UI update

- Installed `okuma-touchpad.desktop` and the bundled SVG icon in the user's XDG
  data directories. `desktop-file-validate` passed.
- Launched the desktop entry using `gtk-launch okuma-touchpad`; the real panel
  opened and populated all 23 saved settings.
- Replaced platform-default form controls with Omarchy's shared popup surface,
  buttons, toggles, dropdowns and text fields. Typography follows the RAM Checker
  panel's Style tokens and bar font. Category tabs reduce vertical clutter.
- Live geometry on the current 800-logical-pixel-high output: card height 617,
  top margin 91, bottom margin 92. The settings area scrolls inside the card.
- Fixed a live QML load error caused by assigning Flow's read-only implicitHeight.
  The final loaded version opens successfully with no new Touchpad QML errors in
  the checked journal interval. Existing saved gesture preferences were preserved.

## Still requires human acceptance

- Physical swipes, pinch/spread, scrolling direction and three-finger dragging.
- Interactive manipulation of every control using mouse, touchpad and keyboard.
- Theme/language changes, small screens and multi-monitor behavior.
- Other hardware, including Windows-origin precision touchpads and external devices.
- Live fault-injection rollback (portable rollback tests pass; failures were not
  deliberately injected into the user's live desktop).
- Omarchy community/official submission and approval.

Use `testing.md` before release. Do not describe this development version as fully
hardware-tested or officially accepted. Local backups and saved desktop settings
are private and must not be committed to the public repository.
