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

## Recovered Codex diagnosis (2026-10-24; read-only runner execution)
Workflow: https://github.com/noxare/night-city-underworld/actions/runs/40103598432

Codex successfully read prior local diagnostic session information and game/Windows logs. It did **not** change any game files or launch the game.

- Game version 2.50, executable 3.0.88.46235; RED4ext v1.30.0 initialized successfully.
- At 2026-10-23 21:55–21:56, RED4ext loaded 0 plugins, compiler succeeded, and shut down normally.
- At 22:45:49, ArchiveXL 1.27.5 began startup; matching Windows 0xc0000005 crash.
- At 22:47:49, Codeware 1.20.6 began startup; matching 0xc0000005 crash.
- At 22:49:39, TweakXL 1.11.5 began startup; matching 0xc0000005 crash.
- No single DLL proven responsible. Shared plugin ABI/address map incompatibility with 2.50, mismatched plugin/SDK builds, or third-party 2.5 patches are plausible. BEX64/StackHash and unknown fault module are not a root-cause determination.
- Current active ArchiveXL has a **different hash/build** from disabled ArchiveXL, despite both reporting 1.27.5: build suffix `2610231736` versus `2610192005`. This changed active DLL and later RED4ext files have **not been game-tested**. Folder duplication outside the active plugin directory does not itself prove duplicate loading.
- A local Graphify report was found by Codex, but it was not committed to the GitHub repository.

Next test (interactive Windows user session): verify game launches to fully rendered main menu with CET still disabled, RED4ext enabled, and only currently active ArchiveXL; observe menu responsiveness for 60 seconds and check fresh crash and RED4ext logs. If it fails, relocate that ArchiveXL to a uniquely named holding directory, test RED4ext without plugins again, restore the files. Compare upstream compatibility and provenance before installing any replacement binaries; do not use unverified unofficial builds automatically.
