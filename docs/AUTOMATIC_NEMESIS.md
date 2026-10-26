# Automatic Nemesis encounter — repository-only development

## Accepted interaction model

2026-10-26: shoot an eligible NPC -> identify that actual actor and anatomical hit evidence -> promote to a durable Underworld person -> store "V injured me" -> request injury/escape behavior automatically. There is no spawn/limb/flee button sequence in the normal UI.

"Static" means a fixed person in the Nemesis simulation, NOT frozen position or an immortal engine entity. While physically present, the game owns position. After the body is confirmed gone, the simulation owns position. A future approach to the simulated location may reserve one new body for the SAME person, with the SAME verified visual identity, remembered relationship and injuries.

A record ID describes an archetype, not a unique person. Initial actors sharing a record are separate people. Recycled/retired entity bindings cannot silently impersonate the earlier person.

## Implemented in this development branch

- underworld/nemesis.py: SQLite person ledger with explicit save slot/timeline, schema version, transactional promotion, conflict-checked event replay, per-person V memories, appearance snapshot, body binding and injury intents.
- underworld/nemesis_mailbox.py: separate encounter IPC. Does not use the synthetic Mara/demo context. Original NPC mutation waits for a durable promotion acknowledgement. CLI requires slot, timeline and game-load session.
- mods/night_city_underworld/encounters.lua: automatic ScriptedPuppet.OnHit observation. Uses the HIT ACTOR, never a later crosshair target. Accepts direct player-instigated non-area hits on crowd NPCs; excludes the old manual test clone. Missing/mixed anatomical data remains unknown.
- HitShapeUserDataBase anatomical predicates are based on the inspected PDO/vanilla approach. CET exposure and exact runtime behavior on the installed version remain unverified.
- The original actor is retained, never replaced, deleted or converted to a follower on first hit. Leg status requests and MoveTo escape requests follow a saved acknowledgement. Native AI owns the original's animation graph; the adapter does not force/reset wrapper weights on that vanilla actor.
- Arm/torso/head guard intents are recorded, with explicit unsupported-posture diagnostics; there is no claim those visual adapters are complete. Two injured legs do not fall back to healthy Run.
- Bounded JSONL trace (1 MiB plus one rotated file), bounded pending outbox, effect presence readback, role/workspot observations, command activity, actual speed/displacement, lifecycle/error events.
- When actor resolution/attachment is lost, a body-ended event can move the persistent person into simulated state with the last measured/captured position. An original is never deleted just because tracking stops.
- Engine-independent offscreen movement advances only simulated people using explicit simulation time and a supplied destination. Illustrative model speeds distinguish healthy escape and injured escape; these are NOT measured native animation speeds or a navmesh route planner.
- Preload reservation checks distance, known offscreen placement, verified navigation, caller budget and identical-appearance reconstruction capability. One lease per person prevents concurrent duplicate spawns. Late/expired acknowledgements need reconciliation. Spawn failure requires proof no body exists. Dead people cannot be resurrected.
- Default CET window is read-only automatic status. Old clone buttons remain in the development module but are hidden behind debugTools=false.
- Future Lua packaging includes encounters.lua while preserving runtime files. No installer or framework has been executed on the gaming PC in this turn.

## Not yet a completed game milestone

1. **Actual view-driven LOD integration:** the core state transitions and spawn lease logic exist; no proven installed-version camera/frustum/occlusion adapter is wired. Currently the runtime detects detach/unload rather than proactively removing a merely offscreen actor.
2. **Same appearance restoration:** runtime captures record, root template and current appearance; this may not capture all randomized components, outfit/equipment or seeds. It sets reconstruction_verified=false. Therefore real rematerialization is deliberately blocked until a tested visual reconstruction profile supplies sufficient data. No random face fallback.
3. **Native materializer:** reserve/confirm/failure interfaces are tested in the core. The engine driver for tagged replacement bodies after confirmed original disappearance is not wired. No second body is spawned by encounters.lua.
4. **Save/load generation:** worker context is explicit operator input. A reliable game-load hook must supply a new session nonce per load, keep it across CET reload and reconcile old bodies/persons. There is no automatic real-save detection. Do not reuse a nonce for another load/campaign.
5. **Offscreen director:** deterministic position advance is an API, not a running autonomous district scheduler. Game-time pause, route/destination selection and area preloading still need the director/engine port.
6. **Visible gait and speed:** native leg status/escape calls are implemented as requests, not a verified limp. Injury-limited native flight speed, both-leg behavior, and arm/torso/head visuals remain unverified.
7. **Eligibility scope:** only crowd actors initially. Ordinary quest/community/essential NPCs are not automatically adopted. Expanding this requires a protected-actor policy.
8. **Session reuse uncertainty:** retired bindings fail closed. The adapter must acquire a new proven generation rather than merge a recycled crowd ID.
9. **Queue durability limits:** complete outbox snapshots are bounded, but a crash during a direct file write can leave a truncated snapshot; the saved request and SQLite replay are additional protection, not an exactly-once event-capture guarantee. A journal/atomic outbox upgrade remains necessary before release.
10. **Recovery ownership:** original effects introduced by this experiment are removed when its local adapter releases the actor; the persistent injury intent is retained in the person ledger. A production lease must reconcile native/external injury owners and treatment instead of treating adapter shutdown as treatment.

These limitations are release gates, not manual actions to ask the user to click around.

## Local verification

Tests in test_nemesis.py, test_automatic_encounters.py, test_npc_probe.py and test_cet_installer.py cover:
- persistent promotion/restart, same-person replay, V memory and save isolation;
- shared archetypes, conflicting payloads, retired entity reuse and load-session mismatch;
- unknown zones and two-leg escape policy;
- offscreen position transfer, simulation ownership, same visual snapshot and no duplicate spawn;
- dead/late/unverified-appearance spawn rejection;
- actual file IPC and replay after worker restart;
- a real Lua VM with mocked CET APIs: automatic original-hit capture, anatomical source, durable acknowledgement gate, wrong-context acknowledgement rejection, no clone/delete and cleanup;
- a normal UI with zero action buttons; reversible packaging preserving outbox files.

Final local command: PYTHONPATH=tests python -m unittest test_nemesis test_automatic_encounters test_npc_probe test_cet_installer -v. Result: 18 tests passed.

No game or Windows runner execution was used. Mocked engine calls do not prove installed-game support.

## Developer-only worker entrypoint (not installed)

python -m underworld.nemesis_mailbox --directory <CET-mod-dir> --database <nemesis.sqlite3> --slot <verified-save> --timeline <branch> --session <game-load-nonce>

This writes an explicit context file for the Lua client. It is not a replacement for game-save discovery and should not be enabled casually while changing saves. The demo bridge continues separately.

## Source provenance

See MOD_SOURCE_RESEARCH.md for exact revisions. New code is original; no third-party mod implementation or game assets were copied. The reviewed Codeware API cannot adopt an existing crowd actor; future rematerialization must occur only after original disappearance and must bind the existing Underworld person, not invent another identity.
