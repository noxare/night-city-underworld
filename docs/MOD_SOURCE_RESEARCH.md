# Mod source research — NPC control, injuries and diagnostics

Research date: 2026-10-26. This is a source inspection, not verification on our installed game.
User acceptance: only one earlier clone showed a requested animation; the next three tests showed no reliable result. PR #11 did not resolve acceptance. Do not mark the injury/flee milestone complete.

## Source inventory and reproducible revisions

| Project | Inspected revision | Inspected files | What it actually contributes |
| --- | --- | --- | --- |
| Ped Damage Overhaul 2077 (PDO) | 6f24a1aa66af7548bd48d7ee9f6814640bb80fad | Main, DamageUtils, Loop, Utils, Logging redscript files | Hit-shape body zones, per-limb counters, native injury status effects, multi-limb exceptions and state readback |
| Appearance Menu Mod (AMM) | 54272353d7e4a5c85ab32248eff3c2d8d2541cd7 | Modules/spawn.lua, director.lua, util.lua, anims.lua | Asynchronous own-actor creation, explicit role lifecycle, navigation commands, rig filtering, separate workspot pose pipeline |
| Real Talk | 0c7b8b66a69db86465d27cbb2c16427642d8c734 | RealTalkActions.reds, RealTalkDiag.reds, RealTalkIdentity.reds | Conflicting hold/workspot teardown, bounded attempts, actual AI state readback, identity pitfalls |
| Codeware | b56f0f66749a7a54ffa4d1a6c403ddc655a37ca7 | scripts/World/DynamicEntitySpec.reds, DynamicEntitySystem.reds; scripts/Entity/EntityBuilderWrapper.reds | Separate record/template and appearance, managed lifecycle/state queries/listeners, inspection surface |

Public sources:
- https://github.com/HJHughJanus/PedDamageOverhaul2077/tree/6f24a1aa66af7548bd48d7ee9f6814640bb80fad
- https://github.com/MaximiliumM/appearancemenumod/tree/54272353d7e4a5c85ab32248eff3c2d8d2541cd7
- https://github.com/swillunderscore/realtalk/tree/0c7b8b66a69db86465d27cbb2c16427642d8c734
- https://github.com/psiberx/cp2077-codeware/tree/b56f0f66749a7a54ffa4d1a6c403ddc655a37ca7

No third-party implementation code or game assets were copied into Underworld.

## 1. PDO: relevant injury implementation, with important limits

In PedDamageOverhaul2077_Main.reds, the physical hit path reads hitRepresentationResult.hitShapes, obtains HitShapeUserDataBase and invokes damage calculations. It skips projection hits, non-player instigators, area attacks and missing hit data; it has human/boss/quest exclusions. Preserve the original wrapped method. These are conditions to investigate, not a ready-made safe hook for our installation.

DamageUtils classifies head/torso/left/right arm/leg using HitShapeUserDataBase.IsHitReactionZone* functions (approximately lines 279–312). This is stronger provenance for body zones than treating a generic hit animation number as a limb.

ApplyDamageEffects (approximately lines 320–357) checks actual HasStatusEffect before applying CrippledLegLeft/Right. The same native status names are already used in Underworld. Therefore this source does not establish that adding the same effect again fixes our crowd clones.

Important exceptions:
- Right-arm crippling is redirected to the left arm in active code, with an author comment about abnormal right-arm behavior.
- Multi-limb branches remove a leg cripple effect and substitute general Crippled/Wounded in some combinations; the source discusses actors stopping when too many limbs are crippled.
- Native effects are reconciled by MainLoop calling ApplyDamageEffects; its zero-delay callbacks are not a performance design to copy blindly.
- Utils contains a commented-out MakeNPCFlee experiment. It is not a working flee implementation and must not be presented as one.

PDO provides a useful native combat-injury baseline, not a demonstrated persistent limping escape system for arbitrary crowd archetypes. The inspected revision dates to 2024; neither current patch compatibility nor our desired gait follows from source inspection alone.

Logging.reds reads back status effects, model/appearance, entity ID, NPC type, health and injury counters. This is the level of evidence our narrow print messages lacked.

## 2. AMM: actor control and animation are distinct pipelines

Modules/util.lua Util:MoveTo (approximately lines 688–709) builds AIMoveToCommand with a world position, movement type, navigation enabled, distance tolerance and finish-on-arrival. This broadly matches our command construction; it supplies no universal missing Run flag.

Modules/director.lua SpawnActors waits asynchronously for entity resolution before generating a sequence. Director tracks commands separately from actor creation.

Modules/spawn.lua SetNPCAsCompanion (approximately lines 692–735) deliberately clears the old role, installs AIFollowerRole, reattaches AI and changes attitudes/companion state. ToggleHostile explicitly respawns a crowd companion because its role cannot simply be changed repeatedly. These substantial side effects make follower conversion unsuitable as a silent generic escape fix.

Modules/anims.lua uses an animation entity and WorkspotSystem.PlayInDeviceSimple / SendJumpToAnimEnt; StopAnimation releases the device. CheckTargetRig filters target rigs/categories and has explicit options. A successful AMM pose does not establish a navigating injury gait. Our graph/rig compatibility must be inspected independently.

## 3. Real Talk: diagnose the consumer and competing owner

RealTalkActions.reds Leave uses MoveTo Run/Walk toward a point away from the player. Before sending, it cancels its own hold command and prevents later return-home behavior. Follow also releases talking gestures/workspots before requesting locomotion. The source records bounded retries for crowd idles which reattach; continuously fighting a workspot is explicitly avoided.

RealTalkDiag.reds reads behavior arguments, shooting blackboard intent/actual counters, threat tracker and attitude. Its combat-specific fields are not movement diagnostics to copy verbatim. The transferable method is to inspect the state the actual AI consumer reads, alongside physical measurements and correlated command IDs.

RealTalkIdentity.reds is also a cautionary example: its header describes an initially stable entity-ID observation, while later active resolver comments report that observation did not generalize and switch anchored NPCs to record-based keys. That is not proof record IDs uniquely identify all NPCs. In Underworld, keep session entity identity, archetype record and durable Underworld identity distinct. Never merge pedestrians merely because they share a record.

## 4. Codeware: spawning is not AI readiness

DynamicEntitySpec separates recordID/templatePath (mutually exclusive), appearanceName, persistence flags, placement and tags. Our current test copies a source record without explicitly fixing appearance; that is not a full clone of the source's animation setup.

DynamicEntitySystem exposes IsReady, IsSpawned, IsSpawning, GetEntity, IsManaged, tags and listeners. Use a bounded lifecycle state machine, not a fixed delay alone. Entity attachment, AI availability and successful command execution remain separate checks.

EntityBuilderWrapper exposes template/appearance/component inspection. Investigate the working archetype against failing archetypes locally; do not publish extracted game resources.

## 5. CyberScript: independently confirms the pipeline split

Specialist review and direct source inspection: https://github.com/cyberscript77/release/blob/6054a10b6ea8c1837925f2889a9b08dc31b62da9/bin/x64/plugins/cyber_engine_tweaks/mods/cyberscript/mod/modules/npc.lua

spawnAnimationWorkspot and spawnCustomAnimationWorkspot asynchronously create workspot entities and use PlayInDeviceSimple / SendJumpToAnimEnt. The separate MoveTo implementation uses AIMoveToCommand with ignoreNavigation=true. This flag differs from our adapter and AMM; do not bypass navigation merely because another scripting tool does. Companion-role removal is explicitly restricted to non-crowd actors in the reviewed path. No freely navigating injury-gait controller was established from these paths. No general reuse license was established for this release tree; a wiki license does not automatically license release code.

## Evidence matrix

| Hypothesis | Source evidence | Current conclusion |
| --- | --- | --- |
| Different archetypes consume injury wrappers differently | AMM filters rigs; our user saw different results | Plausible; compare actual templates/graphs before asserting cause |
| A workspot or ambient owner blocks movement | Real Talk releases own holds/workspots and bounds failed releases | Plausible; observe our clone's workspot/role before mutation |
| All healthy Run commands are inherently downgraded | AMM and Real Talk use MoveTo movementType; native MoveTo differs from spline handling | Unsupported universal explanation |
| Reapplying native leg status is sufficient | PDO uses same IDs but has gates and multi-limb exceptions | Not established for our clone setup |
| Follower mode is a harmless prerequisite | AMM role, attitude and respawn logic | False as a general assumption; do not silently introduce |
| A pose animation proves navigation-compatible limp | AMM workspot pipeline is separate | False |
| Public source establishes installed-game success | Versions and runtime conditions differ | False; compile/adapter tests and in-game evidence remain required |

## Next coherent engineering bundle

1. Build durable, bounded, per-test JSONL diagnostics before another gameplay claim: session/test ID, build/adapter hash, source record, actual template/appearance, spawn/attachment/AI lifecycle, role/workspot observations, requested command/ID/activity, effect presence, wrapper requests/errors, position/speed/destination distance, interruption, cleanup and terminal outcome.
2. Read states at spawn, before/after each transition and a bounded cadence (e.g. 2 Hz); rotate/cap files and report unavailable APIs explicitly. Never serialize engine handles. Logging errors must not suppress cleanup.
3. Use one curated, reproducible owned actor as a native baseline plus selected crowd archetypes as a separate compatibility matrix. Fix the appearance and placement. Establish healthy walk and healthy Run before introducing injury.
4. Compare effect-only, wrapper-only and combined transitions with actual readback. Release only interventions owned by Underworld. A workspot discovery is evidence, not permission to cancel vanilla quest activity.
5. Investigate installed template/graph differences for pass/fail archetypes. Do not force follower roles, combat, teleportation or per-frame animation to conceal missing support.
6. Internally verify timeout, unload, repeated command, conflicting state, both-leg combinations, treatment and cleanup. Only then deliver a bundled user acceptance.
7. If reliable injured escape needs a dedicated behavior/record adapter, implement that explicit supported scope rather than promising every crowd clone.

## License and reuse record

PDO has no LICENSE in the inspected tree; its Nexus permissions restrict modification/reuse. AMM README refers to the official mod's usage terms rather than granting a general source license. Inspecting and learning does not grant permission to copy their implementations/assets. Real Talk README states MIT for mod code; confirm the grant and preserve attribution before reuse. Codeware carries LICENSE/THIRD_PARTY_LICENSES. This report is original analysis and links, not a code import.

## Work status

Completed: cross-project source inspection and architecture decision record.
Not completed: full template/graph comparison on the Windows installation, durable NPC trace logger, reliable healthy crowd escape, general injured gait or injured escape.
Agent use: animation specialist performed a bounded source review; two earlier research delegations failed on usage limits and produced no completed research. No local model execution is claimed.
