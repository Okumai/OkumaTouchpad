# Configuration reference

Saved preferences: `$XDG_CONFIG_HOME/omarchy/okuma-touchpad.json` (default:
`~/.config/omarchy/okuma-touchpad.json`). Unknown keys and invalid types are rejected.
Every field is available in the panel; numeric bounds are enforced by the helper.

| Key | Default | Allowed values |
| --- | --- | --- |
| `naturalScroll` | `true` | true / false |
| `tapToClick` | `true` | true / false |
| `tapButtonMap` | `"lrm"` | lrm, lmr |
| `clickfinger` | `true` | true / false |
| `disableWhileTyping` | `true` | true / false |
| `threeFingerDrag` | `true` | true / false |
| `scrollFactor` | `1.0` | 0.1–5.0 |
| `workspaceSwipe` | `true` | true / false |
| `workspaceFingers` | `4` | 3, 4 |
| `workspaceInvert` | `false` | true / false |
| `workspaceDistance` | `300` | 50–2000 (integer) |
| `workspaceCancelRatio` | `0.5` | 0.0–1.0 |
| `numericNeighbors` | `true` | true / false |
| `createEmptyWorkspaces` | `true` | true / false |
| `verticalFingers` | `4` | 3, 4 |
| `swipeUp` | `"bar-hide"` | none, bar-hide, bar-show, bar-toggle, launchpad-open, launchpad-close, launchpad-toggle |
| `swipeDown` | `"bar-show"` | none, bar-hide, bar-show, bar-toggle, launchpad-open, launchpad-close, launchpad-toggle |
| `pinchFingers` | `4` | 3, 4 |
| `pinchIn` | `"none"` | none, bar-hide, bar-show, bar-toggle, launchpad-open, launchpad-close, launchpad-toggle |
| `pinchOut` | `"none"` | none, bar-hide, bar-show, bar-toggle, launchpad-open, launchpad-close, launchpad-toggle |
| `threeFingerSpread` | `"none"` | none, bar-hide, bar-show, bar-toggle, launchpad-open, launchpad-close, launchpad-toggle |
| `pinchThreshold` | `0.1` | 0.1–0.5 |
| `launchpadPlugin` | `"okuma.dev_launchpad4omarchy"` | Plugin ID: letters, digits, dot, underscore, hyphen; no double dots |

The schema is defined once in `touchpad.py` (`FIELDS`) and shared by the CLI and
panel. `describe` returns this schema, saved preferences and a live application
status (loader digest plus effective global options). Example JSON profiles contain
all fields to make behavior explicit. Launchpad actions are opt-in; an unavailable
Launchpad produces a warning without blocking independent settings. Existing saved
profiles are not rewritten when defaults change.

Primary three-finger pinch suppresses the extra three-finger spread registration.
Disabling a binding means this project does not register it; it does not erase
other applications or external configuration. Existing literal user registrations
are refused before applying, including unrelated ones.

Natural scrolling changes both axes according to Hyprland/libinput behavior; there
is no independent vertical-only inversion in this project. Workspace inversion is
independent. The scroll multiplier affects the global touchpad baseline; app-local
multipliers can still apply.

No user-defined command strings are accepted. Gesture actions are an allowlist.
Changing the Launchpad plugin ID requires a compatible target implementing the
`status`, summon, hide and toggle contracts.
