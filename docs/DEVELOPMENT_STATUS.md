# Development and crash recovery status

## 2026-10-26 — Source research and failed crowd acceptance

- User reports the latest three tests produced no reliable injury animation/escape. PR #11 policy synchronization and activation-edge wrapper binding are installed but have not passed gameplay acceptance.
- Cross-project source review completed: PDO, AMM, Real Talk, CyberScript and Codeware. Revision-pinned findings and the next engineering bundle are in [MOD_SOURCE_RESEARCH.md](MOD_SOURCE_RESEARCH.md).
- No verified universal crowd limp/flee solution was found in the inspected paths. Existing code reveals multi-limb exceptions, competing workspot/hold ownership, explicit companion-role side effects and rigorous state readback.
- Next work: durable per-test traces, a reproducible owned actor baseline, comparison against failing crowd templates, then a supported navigation/injury adapter. No further gameplay fix or logger deployment is claimed by this documentation update.


## Installed wounded-locomotion adapter package 0.0.5

- Installed audit completed with actual resource matches and successful behavior JSON conversion; metadata inspection resolved woundedLocomotion_l_leg/r_leg wrapperName fields in ApplyAnimWrappersOnWeapon tasks, conditioned by WoundedLeftLeg/RightLeg. Exact installed identities and hashes: docs/INSTALLED_WOUNDED_LOCOMOTION.md.
- Important provenance correction: CLI -gp loads game context; archive labels in the audit manifest are requested command contexts, not verified physical resource origin. No game binaries or full converted JSON were committed.
- PR #10 merged as a347219. Native wrapper-weight calls now target only the owned clone at controlled injury/movement transitions, wait for attachment, use one-leg priority, reset weights on treatment/cleanup and measure actual speed. This supplies a native graph binding that the earlier Walk/Run experiments lacked.
- Windows CI passed; installation succeeded: https://github.com/noxare/night-city-underworld/actions/runs/40233757276 . GUI build0.0.5, wire protocol still0.0.2. No game restart was performed; CET reload loads the new Lua.
- Visible asymmetric injured gait, an appropriate injury-limited flee speed and native AI interaction remain unverified. No completed limping capability is claimed from mocked tests or successful deployment. One bundled game acceptance is healthy walk -> selected injured leg -> injured walk -> flee -> treatment -> cleanup.


## Animation asset investigation — active milestone

- Installed WolvenKit GUI found, no standalone console initially. Official WolvenKit9.1 Console is now provisioned under LOCALAPPDATA/NightCityUnderworld/tools with release SHA-256 verification. Actual binary is WolvenKit.CLI.exe.
- Console requires .NET10; system has6/9. Official .NET10.0.14 runtime was installed only in the tool folder with Microsoft release-metadata SHA-512 verification. No system runtime or game archive modifications.
- Actual installed CLI help confirmed: unbundle supports -p/-o/-gp/-r; JSON conversion is convert serialize, not legacy convert -s. Successful tooling run: https://github.com/noxare/night-city-underworld/actions/runs/40232380146 . Long-path support is disabled; audit uses a shortened isolated output path rather than changing OS policy.
- Bounded extraction/manifest helper and two tests implemented. It searches exact hit_reactions/wounded_entry_se behavior and humanoid graph basenames, preserves archive provenance, limits size/time and keeps original/converted game assets local only.
- Installed-resource audit: https://github.com/noxare/night-city-underworld/actions/runs/40232599116 . Result must be inspected before claiming a native injury behavior path is resolved. No new limp implementation or visual verification is claimed by this tooling work.


## NPC observation package installed — 2026-10-25

- PR #6 merged as 4149c58. GUI build 0.0.3 / wire version 0.0.2 integrates opt-in target/hit telemetry, session-scoped observation persistence and dashboard 0.2.0.
- Windows dashboard deployment succeeded: https://github.com/noxare/night-city-underworld/actions/runs/40216909690 . Bridge deployment including controlled worker restart and owned Lua module installation succeeded: https://github.com/noxare/night-city-underworld/actions/runs/40216909652 .
- No user game restart performed. New Lua module loads on a subsequent CET reload; existing active Lua state is not assumed to have changed automatically.
- Automated local tests cover raw snapshot ingestion through the observation DB to dashboard output, probe opt-in/cleanup/filtering/budgets, injury rules and existing bridge regression. Actual 2.5 hit callback delivery remains unverified until genuine telemetry arrives.
- No body-zone mapping or forced injury animation is enabled. Injury reducer is a tested foundation, not proof of in-game limping. Existing demo data and game saves remain separate.


## 2026-10-25 bundled NPC observation implementation

- User verified the earlier CET-to-Python event path and shipment/clinic chain in the dashboard. Earlier entries below saying no CET acknowledgement was confirmed are historical.
- GUI build 0.0.3 adds opt-in read-only target/hit observation; wire protocol remains 0.0.2. Safe target cleanup and bounded raw collider telemetry are integrated without AI/animation mutations.
- Worker ingests observations into a separate versioned SQLite database, with session-only identity, validation, deduplication, stale rejection and source/receipt timestamps. Dashboard 0.2.0 displays actual session observations separately from synthetic contacts.
- Injury reducer implements replay/context/provenance guards, treatment and explicit death outcomes. It does not infer body zones from generic damage or apply animation intents. No persistent limp capability has been proved yet.
- Local targeted tests passed across injuries, NPC Lua probe, observations, dashboard, existing bridge integration and installer. Windows CI and runtime deployment are verified separately; no user micro-step acceptance requested.


## Bridge 0.0.2 Windows deployment receipt

- PR #4 merged. Windows CI: 20 tests passed, 2 explicit system-Lua skips. Real Lua-client-to-Python/SQLite integration passed separately on the development host.
- Deployment succeeded: https://github.com/noxare/night-city-underworld/actions/runs/40157298545 . Runtime installed outside the checkout; separate Python worker started and returned a live `snapshot` acknowledgement from the deployed mailbox (reputation 0, no events).
- Lua files hot-deployed with backup; no game restart or framework change. User told to choose CET Reload all mods, close/reopen overlay, confirm Bridge 0.0.2 and Python-Kern: verbunden, then click Kontakt helfen.
- Post-deployment read-only verification succeeded: https://github.com/noxare/night-city-underworld/actions/runs/40157376210 . Worker process alive after CI cleanup, version 0.0.2, heartbeat age ~0.33 seconds. Latest response was still deployment's synthetic snapshot; no CET-originating BRIDGE_ACK confirmed yet. Do not infer the in-game roundtrip from deployment verification. Start/stop helpers: LOCALAPPDATA/NightCityUnderworld. Campaign synchronization still pending.


## 2026-10-25 Bridge 0.0.2 implementation

- User confirmed Prototype 0.0.1 displayed/worked in-game. This verifies the previous CET module, not yet the new external-core bridge.
- Replaced active Lua simulation with a thin file-IPC client. Version 0.0.2 sends a single durable request and displays only acknowledged Python/SQLite state; no optimistic reputation changes.
- Python mailbox worker reuses LocalBridge and WorldStore, checks intel-chain preconditions, bounds messages and demo events, provides heartbeat and protects the mailbox with a single-worker lock. Replay, restart, pending CET reload, context mismatch and corrupt/partial messages are covered.
- Local integration test executes the real Lua client, serializes actual JSON through files, processes it in Python and checks SQLite plus displayed returned values. Separate subprocess tests verify an independent Python worker and duplicate-worker rejection. The Lua harness mocks CET/ImGui and uses system Lua 5.4; actual CET acknowledgement remains a separate in-game check.
- Demo context is explicitly isolated from campaign saves; no game-save reconciliation or real NPC actions. Old 0.0.1 journal is preserved and not silently imported.
- Deployment now permits hot replacement of only owned Lua files while the game runs. Runtime is installed outside the CI checkout under LOCALAPPDATA/NightCityUnderworld/bridge/0.0.2; start/stop helpers live in LOCALAPPDATA/NightCityUnderworld. Worker persists beyond deployment but does not autostart after Windows reboot yet.
- Deployment/Windows CI result must be recorded separately. User instruction after deployment: CET Reload all mods, close/reopen overlay, verify Bridge 0.0.2 / Python-Kern: verbunden. See docs/BRIDGE_TEST.md.


## Verified installation receipt — 2026-10-25

- First CET prototype merged in PR #3 and installed on STEAMBOX. Installer and SHA-256 verification succeeded: https://github.com/noxare/night-city-underworld/actions/runs/40155690515 . Existing Underworld files are backed up under the local Documents/Underworld-ModBackups folder; stale OneDrive Documents redirection was avoided.
- Read-only diagnostics found the prior CET launch ended with `Unknown Game Version, update the mod`; no Underworld INIT/DRAW markers existed yet.
- Official upstream CET v1.38.0 explicitly supports Cyberpunk 2.5 / executable 3.0.88.46235. Downloaded the pinned official release asset, verified its published SHA-256, installed and verified package files with backup/rollback and preserved existing settings/user mods. Successful update: https://github.com/noxare/night-city-underworld/actions/runs/40155857591 .
- Source: https://github.com/maximegmd/CyberEngineTweaks/releases/tag/v1.38.0 . Archive SHA-256: 6da2e91b07d5ea9dd4aa32145b2c2920a976abee481854976e2ae82169b612e1.
- Windows prototype CI passed 13 tests with 1 explicit skip (system Lua unavailable); Lua rule and mocked entrypoint checks passed separately on the development host. Framework updater's 3 targeted tests passed locally and on Windows.
- No game was launched by these workflows. User should now launch normally, open CET and test the prototype panel; fresh INIT/DRAW/PLAYER_READ log markers and visible behavior remain unverified. Do not treat installation success as engine verification.


## 2026-10-25 first installable CET sandbox

- PR #2 merged after Windows CI passed. Prototype 0.0.1 adds an ImGui panel, read-only V-coordinate probe, synthetic contact reputation and contact -> shipment -> clinic clue chain.
- No spawning, AI control, quests or Python-sidecar connection. Demo journal is one global mod-local test profile, versioned, duplicate-safe and limited to 100 events; no campaign save synchronization. Corrupt/incomplete journal blocks further writes.
- Installer backs up owned Lua files, checks hashes, rolls back failed copies and preserves journals/unrelated mods. Windows installation workflow refuses to install while Cyberpunk is running.
- Three local installer tests and actual Lua rule/syntax test passed. System Lua 5.4 is not CET LuaJIT; Windows CI explicitly skips the Lua test if unavailable.
- Installation and CET INIT/DRAW/PLAYER_READ evidence require separate verification. Do not infer visible in-game success from installation CI.
- Instructions: docs/INGAME_TEST.md. Next: inspect fresh CET logs after launch, then reconcile campaign save context and connect the external core before real persistent NPC events.

The following sections record earlier evidence and historical status.

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

## 2026-10-24 unofficial 2.5 patches staged
The GitHub Windows runner verified that the downloaded unofficial RED4ext and ArchiveXL DLLs exactly match the installed copies (SHA-256). Codeware and TweakXL did not match because their patched DLLs were absent from the active directory. The runner then extracted the exact downloaded Codeware and TweakXL patched packages, including Scripts and Data, into the active `red4ext/plugins` paths while game was not running. Successful workflow: https://github.com/noxare/night-city-underworld/actions/runs/40104276245 . Reversible backup location reported as `C:\Users\Steam\Documents\Underworld-ModBackups\20261024-165020` (existing overwritten files backed up; newly created plugin files had no previous active version). CET stays disabled. No game was launched or menu verified after staging. **NEXT**: User to launch the game normally in the interactive session and verify responsive main menu. Review fresh RED4ext and Windows Application logs before enabling CET, and if crash occurs disable only newly enabled Codeware and TweakXL and retry ArchiveXL-only baseline. Never infer a successful game test from installer workflow success.

## 2026-10-24 first post-patch launch evidence
Workflow https://github.com/noxare/night-city-underworld/actions/runs/40104886627 inspected game launch at 16:57 local: RED4ext initialized, loaded ArchiveXL, Codeware and TweakXL (3 plugins), and unloaded all three on orderly shutdown about 50 seconds later. Two Python unit tests passed. CET was previously re-enabled, but its overlay functionality and a visually responsive main menu have not been directly confirmed in this run. Next work: verify CET Lua execution and implement first minimal in-game event bridge, protecting vanilla logic. Avoid reporting success of CET without its own log/test.

## 2026-10-24 Work: local bridge and development playbooks

- Added `underworld/bridge.py`: explicit slot/timeline binding, protocol v1 JSONL stdin/stdout, bounded messages, duplicate acknowledgement and conflicting-event rejection. No CET/game hooks yet.
- Store now marks schema version 1, preserves prototype schema-0 event records and rejects newer database schemas.
- Local verification: `python3 -m unittest discover -s tests -v` passed all 10 tests. Separate subprocess smoke verified an event stays at reputation 15 after process restart and duplicate replay. Windows CI result must be checked separately.
- `docs/PLAYBOOKS.md` defines small-model routing, escalation, crash diagnosis, scoped verification and handoff. A smaller model drafted the playbooks; the main model reviewed them and implemented the protocol/persistence work.
- `docs/LOCAL_BRIDGE.md` documents runnable commands and limits. Timeline isolation is not game-save rollback: new timelines start empty, and automatic campaign integration is explicitly deferred.
- Next: verify CET Lua execution in interactive Windows; inspect current primary CET APIs; implement bounded nonblocking game transport and synthetic event roundtrip, then reconcile save/load snapshots before enabling real gameplay writes.
