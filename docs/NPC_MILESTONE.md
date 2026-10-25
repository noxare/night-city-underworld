# Bundled NPC milestone — implementation work in progress

User acceptance is requested only for a coherent end-to-end milestone, not each
internal implementation step. Continue internal tests and keep implementation,
engine feasibility and in-game verification distinct.

## Completed foundation

- Deterministic injury reducer with schema validation, session/NPC isolation,
  duplicate/conflict rejection, evidence budget, treatment and explicit lifecycle
  outcomes. Generic damage never invents a body zone. Visual intents report engine
  capability separately; they do not apply animations.
- Opt-in read-only Lua NPC probe module: targeting, session-scoped entity hash,
  bounded hit-counter/collider-tag evidence and bounded diagnostic snapshot file.
  It retains scalar data only, not NPC/player handles. No AI/quest/animation writes.
  The milestone client integrates protected module loading and opt-in start/stop
  controls; raw hit observations are consumed by Python and persisted separately
  from test-contact reputation. The dashboard shows session actors, observed hit
  counts and raw collider provenance without asserting an anatomical mapping.

## Remaining integration gates

- Completed in code: probe enable/disable, target/unload cleanup, diagnostics UI,
  SQLite observation storage and separate dashboard table. Windows runtime proof
  and genuine in-game hook execution remain distinct from mocked tests.
- Verify current hook and field availability on Windows; use actual collider tag
  observations to establish a documented body-zone mapping. Unknown remains unknown.
- Completed in code: separate observation persistence, strict validation, bounded
  actor count, stale-message rejection and deduplication with receipt timestamps.
- Prove a supported locomotion-compatible injury animation and interruption/cleanup
  pathway. No generic animation name, body-part enum or persistent limp hook is
  assumed to exist. Workspot animation is not proof of safe walking/limping AI.
- Resolve game save/load identity and rollback before claiming durable crowd NPCs.
- Deliver one complete NPC observation -> evidence -> injury -> visible behavior
  scenario once all required engine capabilities are verified. No intermediate user
  test request is needed for the core modules.

## Primary API evidence and uncertainty

- Codeware author target example: https://gist.github.com/psiberx/50bcf9368cfeff5937de1a1ed815bdb1
- Callback documentation: https://wiki.redmodding.org/scripting-cyberpunk/scripting/game-systems/events-and-callbacks
- Codeware source: scripts/Base/Addons/gameHitEvent.reds (hitColliderTag) and
  animation HitReactions fields in psiberx/cp2077-codeware. These expose raw fields,
  not a verified anatomical enum mapping or persistent gait-control capability.
- Historical hitShapes examples may not match current 2.5 RTTI and must not be copied
  blindly. Probe registration succeeding does not prove callbacks fire in-game.

The 0.15 normalized damage threshold is a provisional simulation tuning parameter,
not a measured game rule. Test fixtures must never be presented as game telemetry.

## Delivered observation package

GUI build 0.0.3 preserves bridge protocol version 0.0.2. After installation, CET
Reload all mods loads the NPC module; its capture is off until explicitly enabled.
The dashboard 0.2.0 shows "NPC-Beobachtungen aus dem Spiel" separately from demo
contacts. Entity IDs are session-only; the probe follows the currently looked-at
NPC and counters describe the current target observation. No animation is forced.
Worker and dashboard upgrades restart only their own application processes, not
the game. Existing reputation events, campaign saves and demo journals are preserved.
