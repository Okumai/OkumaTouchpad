# OkumaTouchpad

A configurable native touchpad integration and settings panel for the Omarchy
Quickshell desktop. It brings touchpad preferences, continuous workspace swipes,
bar gestures and optional Launchpad pinch actions under one owner.

**Status: early development, prepared for community review; not an official or
approved Omarchy plugin.** Portable tests and manifest validation do not establish
physical gesture support or a successful live QML session on every device.

All source, documentation and default interface strings are English. Interface
strings use Omarchy's translation API with an English fallback catalog.

## Design

- Native recognition through Hyprland and libinput: no raw-input daemon, root
  permissions, input-group membership or event-device access.
- A theme-aware panel with editable settings, Lua preview and diagnostics.
- Explicit Apply: opening/enabling/updating the plugin never rewrites gestures.
- One separately generated user Lua file, a marked loader, timestamped backups,
  effective-setting checks, and rollback after failed validation.
- Conservative conflict detection; no automatic deletion of personal bindings.
- No network calls, telemetry, background polling or downloaded executable code.
- Enabling the plugin registers its user-owned application entry, even when installed
  with Omarchy's git installer. It never applies input settings on startup.

## Requirements

- Omarchy with its plugin-enabled Quickshell desktop, `qs.Commons.Translations`,
  and the documented shell IPC interface.
- Hyprland with the native `hl.config` / `hl.gesture` Lua API and
  `input:touchpad:drag_3fg` support. This targets the API used by the development
  desktop (Hyprland 0.56.2); other versions require validation and testing.
- Python 3.10+ on Linux. Tests optionally use Lua to exercise callbacks.
- A touchpad/driver reporting the selected gesture types and finger counts.
- Optional: an enabled compatible OkumaLaunchpad for Launchpad actions. Pinch
  actions default to `none`. Missing Launchpad produces a warning, not a failure of
  independent touchpad/workspace/bar settings. Dependencies are not installed automatically.
- Legacy `hyprland.conf` sessions are not supported. An incompatible compositor is
  reported explicitly; no successful apply is claimed.

## Installation

Review the source first: Omarchy plugins execute unsandboxed as your user.

Recommended, git-managed installation:

```bash
omarchy plugin add https://github.com/Okumai/OkumaTouchpad.git --enable
# Future updates:
omarchy plugin update okuma.dev_touchpad4omarchy
```

The plugin registers its desktop entry when enabled. Omarchy's installer does not
execute repository installation scripts; this registration is handled by the panel
itself and changes only the user application entry/icon, never gesture settings.

Alternatively, install a reviewed local snapshot:

```bash
cd /path/to/OkumaTouchpad
python3 install.py
# Unattended installation after source review:
python3 install.py --yes
```

This validates and installs a local snapshot at:

```text
~/.config/omarchy/plugins/okuma.dev_touchpad4omarchy/
```

It enables the panel and checks its IPC response. It does **not** change input
settings, add keybindings, install dependencies, or migrate existing gestures.
Existing installations are reused unless a snapshot update is requested explicitly:

```bash
# From an updated source checkout, replace an old local snapshot with backup:
python3 install.py --update
```

The previous snapshot is retained under `~/.config/omarchy/plugin-backups/`.
Git-managed checkouts are never overwritten by this option; use the supported
`omarchy plugin update` command instead. A local snapshot is not automatically
git-updatable. If an updated panel remains stale after hot reload/rescan,
deliberately run `omarchy restart shell`; the installer does not force this
potentially disruptive step.

Open **OkumaTouchpad** from your system Applications list or Launchpad. The installer
and plugin enable/load both ensure a user-owned desktop entry and bundled touchpad
icon are present; no terminal is needed after installation.
The launcher respects `XDG_DATA_HOME` (default `~/.local/share`).

The centered panel uses the same Omarchy typography, popup border, buttons, toggles
and dropdowns as the RAM Checker panel. Category tabs keep related preferences
together. Its height is capped with symmetric top/bottom safe margins (at least
80 theme-scaled logical pixels, increased for bar size and screen height), and
settings scroll inside the card rather than extending into the topbar or Dock.
On the current desktop it leaves approximately 91 logical pixels on each side.

Command-line fallback:

```bash
omarchy-shell shell summon okuma.dev_touchpad4omarchy '{}'
```

Use **Preview**, review conflicts and settings, then **Apply and save**. **Reload
saved** discards the draft. **Diagnostics** inspects saved settings, not the draft.
The status line distinguishes unapplied settings, verified saved settings and failed
operations. A failed Apply retains the draft and shows the error; it is not a save.
No input configuration is applied on shell startup, plugin hot reload or update.

## Defaults and customization

The initial preset is independent of Launchpad and avoids a three-finger
pinch/drag conflict. It does not import the development device's private files or
guarantee identical hardware behavior. Existing saved profiles retain their actions.

| Category | Default | Customization |
| --- | --- | --- |
| Scroll direction | Natural | Natural or traditional |
| Touchpad scroll multiplier | 1.0 | 0.1–5.0 |
| Tap to click | Enabled | On/off |
| Tap order | `lrm`: one left, two right, three middle | `lrm` / `lmr` |
| Physical click finger counting | Enabled | On/off |
| Disable while typing | Enabled | On/off |
| Three-finger drag | Enabled | On/off |
| Horizontal swipe | Four fingers, continuous workspace switching | Enable, 3/4 fingers, invert, distance, cancellation ratio |
| Workspace neighbors | Numeric, empty neighbors allowed | Each independently configurable |
| Vertical up / down | Four fingers, hide / show bar | 3/4 fingers and separate action choices |
| Primary pinch inward / outward | Disabled (four fingers when configured) | 3/4 fingers, separate actions, scale threshold |
| Extra three-finger spread | Disabled | Any supported action or disabled |
| Launchpad target | `okuma.dev_launchpad4omarchy` | Validated plugin ID |

Action choices: `none`, `bar-hide`, `bar-show`, `bar-toggle`, `launchpad-open`,
`launchpad-close`, `launchpad-toggle`. Deliberately no arbitrary shell-command
field: settings cannot inject shell commands or Lua source. Workspace switching
uses Hyprland's continuous native action rather than repeated shell commands.

### Natural versus traditional scrolling

Choose behavior, not the computer's brand: users can change scrolling preferences
on both Windows and macOS. With **natural scrolling**, content follows the finger
movement; with it disabled, the same motion moves content in the opposite direction.
This is Hyprland's global touchpad setting. It does not invert mouse wheels,
workspace swipes or vertical action bindings. Workspace direction has a separate
**Invert horizontal workspace direction** switch. Hyprland's single natural-scroll
setting is not an independent vertical/horizontal-axis toggle.

Apps can apply their own scroll multipliers; Dock and Launchpad retain ownership
of their internal scrolling, icon dragging and other pointer interactions.

## Configuration and CLI

```text
~/.config/omarchy/okuma-touchpad.json  # Saved, validated preferences
~/.config/hypr/okuma-touchpad.lua     # Generated native config and bindings
~/.config/hypr/hyprland.lua           # Marked dofile loader appended last
```

`XDG_CONFIG_HOME` is respected. `--config-home` can select another configuration
root, but live apply still requires that root's entry point to be loaded by the
current Hyprland session. It is not an offline deployment flag.

```bash
python3 touchpad.py describe
python3 touchpad.py preview
python3 touchpad.py preview --settings-json '{"naturalScroll": false}'
python3 touchpad.py apply --settings-json "$(<examples/settings.json)"
python3 touchpad.py doctor
```

`--settings-json` describes a complete profile: omitted fields use project defaults,
not previous saved values. To modify an existing profile without resetting other
preferences, use the panel or pass the entire updated saved object. The example
profiles are intentionally complete. Settings are saved only after successful
apply; invalid drafts and failed transactions do not replace saved preferences.

See [configuration](docs/configuration.md) for every field and
[migration](docs/migration.md) before taking ownership of existing gestures.

## Safety and limitations

Apply scans all `*.lua` files under the selected user `hypr` directory and refuses
other literal `hl.gesture(...)` registrations, even for otherwise unrelated gestures.
It excludes only its own generated file. This favors a clear single owner over a
potentially incomplete attempt to merge arbitrary executable Lua.

This scan is not a Lua interpreter: computed aliases, registrations in external
includes, symlinked directories and packaged defaults require manual review.
Conflicts or overriding effective settings detected by Hyprland cause rollback.
Always inspect all loaded includes, including files outside the user directory.
Ordinary touchpad preferences remain in personal files; the marked loader appended
at the end of the entry point gives this profile precedence for managed options.

Timestamped `.bak.okuma-touchpad.*` copies are kept beside changed files. Transactions
restore files on handled failures, but are not a filesystem-wide atomic commit and
cannot guarantee rollback after power loss or process termination. Do not edit the
same files concurrently; the lock serializes this project's own CLI operations only.

Three-finger dragging may consume three-finger gestures. With a three-finger primary
pinch, the extra three-finger spread is ignored to avoid registering the same event
twice. Hyprland may gate pinch recognition at roughly 10% scale change; the supported
threshold is 0.10–0.50 and cannot bypass compositor/driver recognition limits.

## Troubleshooting another device

1. Update the **installed** copy, not only a separate source checkout. Restart the
   shell deliberately if it is still running an older panel.
2. For a missing Apps entry, enable the plugin, or run
   `python3 ~/.config/omarchy/plugins/okuma.dev_touchpad4omarchy/launcher.py install`.
   An alternative launcher may need its own cache refresh. Registration failures
   are displayed in the panel rather than silently ignored.
3. Use **Apply and save**, then check the status line and full output. **Reload saved**
   only reads preferences. Failed validation rolls back changes and does not save
   the new profile. Existing gesture conflicts require manual migration; see
   [migration](docs/migration.md).
4. Run the installed helper for diagnostics:

   ```bash
   python3 ~/.config/omarchy/plugins/okuma.dev_touchpad4omarchy/touchpad.py doctor
   hyprctl configerrors
   ```

   This reports the compositor version, configuration root, optional integration
   warnings, loader digest and effective global options. Saved JSON alone does
   not prove that Hyprland loaded it.
5. If global options verify but a physical gesture still fails, check hardware/driver
   gesture support, selected finger count, per-device input overrides and other
   input tools. Three-finger dragging can consume three-finger gestures. Missing
   Launchpad affects only Launchpad actions. The helper cannot establish physical
   recognition remotely or from the pointer device name alone.

## Removal

First remove native bindings while the helper is still available:

```bash
python3 ~/.config/omarchy/plugins/okuma.dev_touchpad4omarchy/touchpad.py remove
python3 /path/to/OkumaTouchpad/launcher.py remove
omarchy plugin disable okuma.dev_touchpad4omarchy
```

`remove` deletes only the marked loader and owned generated file, reloads Hyprland,
and validates configuration errors. It retains preferences and backups. Disabling
or uninstalling the shell panel alone does **not** remove native Hyprland bindings.
Previously migrated personal bindings are not restored automatically: review backups
and restore deliberately if desired. The helper refuses unowned generated files.

## Development and submission

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
omarchy plugin validate .
```

See the [current validation report](docs/validation-status.md),
[CONTRIBUTING.md](CONTRIBUTING.md), [testing](docs/testing.md), and
[publication](docs/publication.md). Live panel loading, all controls, effective
scroll direction, migration and physical gestures must be tested before release.
No installer is run and no desktop settings are changed by the portable tests.

License: MIT.
