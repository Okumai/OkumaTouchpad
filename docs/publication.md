# Publication and Omarchy community review

This is a third-party plugin using Omarchy's manifest contract, not an official
Omarchy component. Manifest validation is necessary but not approval or endorsement.
No submission, repository upload or account action is automated by this project.

## Before publishing

1. Review every source file and dependency. Plugins execute in the user's shell.
2. Run portable tests, manifest validation and QML linting.
3. Complete the desktop and hardware checklist in `testing.md`, recording versions
   and known unsupported devices/gestures. Include panel screenshots and a short demo.
4. Verify install, upgrade, manual migration, rollback and removal in a clean session.
5. Check current Omarchy plugin submission and marketplace requirements with the
   maintainers; the installed package does not include the full shell reference.
6. Set a real public source URL in publication material once the repository exists.
   Do not invent a repository URL or imply an official listing.
7. Review the working tree and history for private configuration, diagnostics,
   credentials, absolute development paths and generated artifacts.
8. Confirm MIT license attribution and English fallback catalog coverage.
9. Tag a tested version and document any changes to settings defaults or managed Lua.
10. Explain the single-owner migration model and optional Launchpad dependency.

Keep the non-reserved plugin ID `okuma.dev_touchpad4omarchy`. A possible future
first-party conversion would be a separate maintainer-reviewed change; do not use
`omarchy.*` IDs for a third-party submission.

## Review points

- No raw-input permissions, privileged installer, network polling or daemon.
- No background rewrite of user input configuration on enable/update.
- Allowlisted actions rather than arbitrary command execution through settings.
- Explicit global scope for natural scrolling and scroll multipliers.
- Conservative conflicts, limited static-analysis claims and visible hardware caveats.
- English catalog with live Omarchy translation fallback.
- Panel uses theme tokens; a future UI polish pass can adopt more shared `qs.Ui`
  controls instead of styled Qt Quick Controls where desired by reviewers.
- No CI workflows are included; checks run locally. Official review may add its own
  validation according to the upstream process.
