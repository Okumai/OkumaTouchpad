# Validation status

## Automated checks

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
