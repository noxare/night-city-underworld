# Development and crash recovery status

Last reviewed: 2026-10-24

## Current phase
Windows-first local simulation MVP. `underworld/core.py` and `underworld/store.py` are prototype code only. Windows GitHub runner `underworld-windows` passes two Python unit tests; no CET bridge or live NPC behavior has been integrated.

## Environment
Windows machine STEAMBOX, interactive user Steam, GitHub runner in `C:\Users\Steam\action-runner`.
Game: `H:\SteamLibrary\steamapps\common\Cyberpunk 2077`, updated to 2.5.
Codex and Graphify executables are installed in user PATH. Graphify outputs and Codex skill directory have not been committed to repository.

## Verified launch-crash history
- With CET and RED4ext loader active, Cyberpunk crashed during startup.
- Disabling CET alone (`bin\x64\version.dll.disabled`) did not fix startup.
- Disabling RED4ext loader as well (`bin\x64\winmm.dll.disabled`) allowed Cyberpunk to start.
- Enabling RED4ext with all `red4ext\plugins` disabled also allowed Cyberpunk to start.
- Therefore, a RED4ext plugin or plugin compatibility interaction is strongly suspected; root cause has not been verified.
- Windows app event log reported `0xc0000005`, faulting module unknown.
- On 2026-10-24, runner observed CET still disabled; RED4ext loader active; `red4ext\plugins` contains ArchiveXL; `red4ext\plugins.disabled` contains ArchiveXL, Codeware, TweakXL. Duplicate ArchiveXL directory entries need inspection before moving files.
- Last manual requested test was RED4ext with ArchiveXL only, not yet confirmed as working.
- Do not claim game reaching main menu merely from process or CI job success.

## Next safe diagnostic
- Inspect local prior Codex session notes and log files (avoid disclosing tokens or unrelated personal data).
- Establish exact installed module versions versus Cyberpunk 2.5 compatibility.
- With user game session idle, execute reversible **one-variation-at-a-time** plugin tests, preserving backups and explicit test result.
- Favor direct confirmation that the game reaches menu, not just absence of Windows crash event.
- Never delete user saves or unrelated mods.
- Record full command, tested config, timestamp, exit status, logs and rollback.

## Automation
- `.github/workflows/windows-runner-smoke.yml`: read-only runner diagnostics and local core tests.
- `.github/workflows/cyberpunk-launch-diagnostics.yml`: launch-crash log inspection.
- `.github/workflows/underworld-recovery.yml`: recovery audit and read-only Codex analysis; check GitHub Actions for its latest outcome.

Update this file after meaningful work so subsequent Codex sessions can resume without chat history.
