# Migrating existing gestures

OkumaTouchpad is intended to become the single owner of a user's global gesture
bindings. Migration is deliberately manual: arbitrary personal Lua must not be
rewritten by a heuristic installer. Installing/enabling the panel is safe before
migration; Apply refuses existing literal registrations.

## From the development layout / OkumaLaunchpad

1. Back up `hyprland.lua`, `input.lua`, and every relevant included configuration.
2. Record current actions, finger counts, scrolling preferences and thresholds.
3. If Launchpad's managed pinch/workspace blocks are present, remove them with its
   documented `setup-gestures.py remove` command, or carefully remove the marked
   blocks after backing up. Its helper does not remove manual workspace bindings.
4. Remove or comment out manual `hl.gesture` workspace and vertical bar bindings
   that OkumaTouchpad will replace. Review other registrations separately.
5. Review all other loaded files, including packaged defaults and external includes.
   The conservative scan covers user `hypr/**/*.lua`, not arbitrary Lua execution.
6. Keep unrelated input preferences. OkumaTouchpad's generated configuration loads
   last and overrides only its supported touchpad/workspace options.
7. Enable a compatible Launchpad before selecting Launchpad actions. To use the
   project independently, change all Launchpad actions to `none` or bar actions.
8. Open OkumaTouchpad, configure the matching profile, Preview, then Apply.
9. Run Diagnostics, `hyprctl configerrors`, and the physical test checklist.

Do not rerun Launchpad's gesture installer after migration. Use its
`--no-gestures` installation option when installing the launcher separately.
The existing Launchpad project has not been modified by this repository.

## Failure and recovery

- Conflict errors occur before configuration writes: review and migrate the listed
  files; do not bypass the check with blind deletion.
- A failed live validation restores the files changed by that transaction and
  attempts to reload the restored configuration.
- Backups have a `.bak.okuma-touchpad.<timestamp>` suffix. Inspect each before
  restoring; backups can contain private configuration and should not be published.
- Manual migration changes are outside the transaction and cannot be automatically
  reconstructed. Restore them from your own backups if abandoning migration.
- If an entry point uses computed includes, alternate configuration roots, or later
  asynchronous overrides, inspect it manually. The live digest verifies the marked
  generated code executed, not every possible future runtime mutation.
