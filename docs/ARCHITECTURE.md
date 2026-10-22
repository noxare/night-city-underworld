# Architecture — Night City: Underworld

Status: design proposal, not implemented. Cyberpunk 2077 / REDengine 4 integration must be validated in-game.

## Principles
- Persistent independent underworld simulation even when V is not present.
- Deterministic, engine-independent simulation core; thin REDengine adapter.
- Save-schema versioning, reproducible seeds, event journal and migrations.
- Three distance levels: distant aggregated strategic ticks, nearby planned encounters, visible bounded spawned encounters.
- Limit spawns, CPU work, combat frequency, duplication and offscreen-to-onscreen transitions. Avoid spawn popping.
- Protect vanilla main quests, essential NPCs and scripted police encounters; dynamically gate mod-authored jobs first.
- Offline/single-player operation; no external service requirement.

## Logical modules
1. Factions: reputation (-100..100), diplomacy, rivalries, truces, alliances, resources, objectives.
2. Characters: stable IDs, gang hierarchy, personality, courage, morale, loyalty, ambition, friends, rivals, leadership succession, memory and nemesis.
3. Combat survival: assess danger; retreat, surrender, flee, protect or rescue allies, request backup; optional cyberware escape maneuvers only on supported navigation.
4. Persistent injuries: damage zones (head, torso, both arms and legs), nonlethal incapacitation, lasting disabilities, recovery, later prosthetics/augmentation. Never infer dismemberment from generic HP loss.
5. Territorial strategy: district/control/influence, patrols, attacks, war, resource shortages; NCPD, corpo security, MaxTac response according to believable threat thresholds.
6. Intelligence graph: provenance, confidence, secrecy, freshness, known-by; witnesses, rumors, hacking, counter-tracing, surveillance, contact revelation.
7. Market/logistics: transport orders, cargo manifests, suppliers, faction economies, vendor pricing and stock.
8. Clinics: independent, gang-affiliated, corporate, hidden illegal ripperdocs; price modifiers, relationship access, quality, black market experimental cyberware and risks; law enforcement.
9. Missions/UI: mod-authored gigs, faction lockouts and redemption paths, Kiroshi scanner expansion and underworld dossier.

## Runtime integration candidates — NOT VERIFIED
- redscript + Codeware for lifecycle/engine hooks and gameplay.
- Cyber Engine Tweaks Lua for prototyping, debug UX and configuration.
- TweakXL / ArchiveXL / VendorsXL for records, new inventories, assets and vendors.
- RED4ext native C++ only if unavoidable.
- WolvenKit for tooling.
Verify exact versions, hooks, license and runtime compatibility before coding to APIs.

## Domain events
CombatStarted, DamageObserved, NpcDowned, NpcEscaped, NpcRescued, NpcKilled, IntelLearned, IntelLeaked, ReputationChanged, TerritoryContested, ShipmentCreated, ShipmentIntercepted, ClinicRelocated, CyberwareInstalled, PoliceDispatched.

## Engineering safeguards
Idempotent event application; stable character identity across respawn/save; save/load cycle tests; configurable difficulty, disabled systems and rate limits; reproducible gameplay logs; selective CI; documented boundaries for NPC/control and quest changes.

## Feasibility unknowns
Engine events for hit zones/nonlethal, AI movement/cyberware traversal and surrender, persistent NPC templates, police dispatch, scanner UI extensibility, dynamic vendor pricing and inventory caching, hidden clinic interiors, mission/quest integration.
