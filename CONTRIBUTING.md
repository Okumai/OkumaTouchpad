# Contributing

Use English for code, comments, default interface strings, documentation and logs.
Keep user-facing text in `i18n/en.json` and use Omarchy's `Commons.Translations`.
Additional language catalogs are welcome; English remains the fallback.

## Principles

- Hyprland owns recognition. Do not add raw event readers or input permissions.
- Applying global configuration must remain an explicit user action.
- Preserve personal configuration and refuse ambiguous ownership or conflicts.
- Keep public actions allowlisted and validate every setting before generation.
- Never interpolate arbitrary settings into shell commands or executable Lua.
- Treat process output and plugin settings as untrusted; display them as plain text.
- Do not modify packaged files under `/usr/share/omarchy`.
- Keep Dock/Launchpad local pointer behavior in those projects.
- Prefer small changes with regression tests and clear migration notes.

Run the checks in `docs/testing.md`. UI changes require live desktop tests as well
as portable checks. Hardware-specific claims need model, driver and version details;
never infer four-finger pinch support from a device listing alone.

See `docs/publication.md` before proposing upstream/community inclusion. This project
has not yet been approved as an official Omarchy plugin.
