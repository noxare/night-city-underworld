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
  This module is not enabled by the current installed CET client yet.

## Remaining integration gates

- Wire probe enable/disable, lifecycle reset and diagnostics into a milestone UI.
- Verify current hook and field availability on Windows; use actual collider tag
  observations to establish a documented body-zone mapping. Unknown remains unknown.
- Persist observed encounters separately from synthetic contacts and expose them
  in the dashboard with session-only identity clearly marked.
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
