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

## Platform strategy (decision 2026-10-22)
- **Windows x64 is the primary development, integration and release target.** REDengine/CET/Codeware and related tooling will be evaluated and tested against Windows first.
- A macOS-native port is a later milestone **after a stable playable Windows release**, not a release blocker.
- Keep domain models, save formats and core decision rules decoupled from Windows-specific game hooks where practical; do not overengineer or maintain an untested macOS game adapter now.
- Windows in-game verification requires an interactive user session; a background GitHub runner can handle non-graphical checks but should not be assumed to launch graphics/game UI reliably.

## Ambient event director
An independent, budgeted Civilian Life & Street Events director schedules nonviolent life vignettes and rare accidents. For each candidate it evaluates territory, traffic/nav/vehicle conditions, quest guards, nearby events, spawn headroom and probability, then instantiates only within supported REDengine facilities. Treat dialogue, animations, vehicle boarding, arrest and police behavior as separate capabilities with explicit feasibility flags. Report chosen and rejected branches to the developer dashboard. Preserve per-zone cooldowns, priority for peaceful resolution, event cleanup and reproducible random seeds.

## Street Cred integration and threat director
Treat vanilla Street Cred as a read-only gameplay signal in the core's player profile. Keep separate faction standing and knowledge/recognition. Evaluate reactions using configurable, inspectable factors (fame, reputation, recognition confidence, NPC morale/power, witness alerts, active hunters and current cooldowns). Emit decision traces for flee/ignore/seek reinforcement/escalate to elite pursuit/help. Rate-limit calls for support and hunter assignments and integrate with quest safety and event budgets. Verify Street Cred read access and level-change notifications on Windows in Phase 0.

## Autonomous hunt and investigation director
A HuntCase references initiating NPC/faction, target (V), motive, budget, current intel confidence, last reliable sighting, candidate contacts, risk tolerance, investigation stage, cooldown and exit conditions. Hunters request IntelActions from the shared intelligence graph; outcomes may produce clues, heat, resource costs, injuries, disputes, law enforcement and reputation changes. Use seeded, logged decision steps for distant investigations and instantiate local encounters only if feasible, relevant and within the shared spawn budget. Record why an action was selected, which intel was updated and why a case escalated, paused or closed. Prevent omniscience, stale-location leaks and repetitive hunter spawns.

## Social graph, NPC finances and adaptive adversaries
Represent durable directed relationship edges with type (kinship, friendship, romantic tie, obligation, respect, hostility), strength, evidence/known-by and timestamps. Model grief/grudges as traceable consequences of perceived events; do not automatically spread facts to every related person.
A PersistentCharacterEconomy includes wallet balance, obligations, recurring income/expense models, equipment inventory, medical liabilities, debts and faction subsidies; a distinct FactionTreasury holds collective resources. Apply ledger-style transactions with source/event IDs and prevent negative balances unless explicit debt is modeled.
An AdaptiveThreatPlanner considers V's fame, identity certainty, faction standing, personal motive, NPC combat strength, cash, suppliers, support and risk tolerance. Possible outcomes: withdraw, negotiate, ambush, request help, acquire gear, train/recover, confront openly, abandon pursuit. Every selected strategy is logged with alternatives, costs and limiting factors.
Performance tiers: full graph/economic behavior only for named persistent NPCs; coarse aggregates for anonymous/background crowds. Add seeded replay tests and invariant checks on wealth transfer, upgrade prerequisites, social-event propagation and anti-spam rules.

## Career, lifestyle and appearance model
A persistent NPC career record has rank, promotion history, authority, compensation rules, privileges and boss/peer evaluations. Feed income changes into the auditable personal ledger and separate necessities, discretionary spending, savings and investments.
AppearanceProfile tracks outfit IDs, style/condition/quality tags, social signals, distinctive body/cyberware markers and history of sightings. RecognitionEstimator combines identity certainty, attire match, face/voice/chrome traits, witness quality, proximity and faction intelligence; clothing change adjusts recognition likelihood, never resets known identity. Distinguish social perception from actual wealth; all appearance updates are limited by available assets and validated game API.
Instrument promotions, shopping, outfit changes and recognition decisions as explainable journal events.

## External simulation runtime / game bridge (architecture candidate, 2026-10-23)
Decision direction: explore a **Windows-local out-of-process simulation service** for strategic/offscreen world logic, coupled to the game by a lightweight REDengine bridge, instead of performing all calculations in engine callbacks. This is a proposal pending IPC and performance feasibility tests, not a shipped dependency.
- External core: NPC and gang financial ledgers, social relationships, strategic ticks, memory, intelligence, offscreen encounters, event sourcing, developer dashboard.
- In-game bridge: read relevant gameplay signals, report visible encounters and combat outcomes, ask for NPC/encounter materialization, apply authorized state updates using main-thread-safe engine facilities.
- Game remains authority on physically simulated combat/collisions/actions; core is authority on persistent abstract state. Explicit ownership and idempotent event IDs prevent double outcomes.
- IPC candidates: loopback named pipes or TCP with local-only binding, versioned protocol, authentication/permissions, bounded queues and retries. A filesystem bridge is a possible limited prototype/fallback. Existing community bridges suggest feasibility but do not prove our required hooks.
- Lifecycle: start/connect with game, pause when the game is paused, distinguish in-game-time ticks from wall clock, clean stop on exit. Never silently simulate days while game is shut down unless explicitly enabled.
- Persistence: save-slot-specific snapshots, migration, session identifiers, reconnection after process crash, protection from duplicated events/rollback after loading old savegames. Validate load/save coherence.
- Reliability: bounded stale messages, backpressure, graceful degraded behavior if sidecar is absent, clear installer/opt-in and removal pathway. No network access required.
- Benchmark IPC latency and spawn/AI interfaces before committing to sidecar architecture; preserve ability to embed compact core logic later if necessary.

## Crowd character promotion and evidence propagation
- Three entity classes: protected vanilla actors (read-mostly with narrowly validated vendor integrations), anonymous transient crowd actors, and Underworld persistent actors (promoted crowd/managed characters). Ownership boundaries are mandatory.
- Promotion pipeline: detect significant interaction -> sample stable reconstructible visual/behavior tags -> allocate Underworld character ID -> store seed, encounter record and appearance snapshot -> generate minimally consistent background/social links -> persist -> later materialize with deduplication, safe spawn placement and engine-supported template.
- Promotion must be idempotent by encounter plus actor/session identity. Engine handles are ephemeral; reconcile entity ownership at stream-out, reload and save rollback.
- Witness graph: observation record (observer/possible anonymous witness, event, location/time, line of sight or approximation, perpetrator confidence, source reliability) -> dissemination by conversations, comms and faction channels -> recipient knowledge and evolving sentiment. Use witness density as one probability factor, never sole determinant.
- Log why an identity was promoted, whether visual restoration is supported, who saw what, who learned what and why the resulting reaction occurred. Bound promotion frequency, retained memories and social-graph growth.

## Civil incident resolution and monetary consequences
Model IncidentCase with actor/victim/witness IDs, injury severity, culpability confidence, evidence, location, jurisdiction, status and proposed remedy. Route outcomes through a staged resolution director (conversation -> compensation/negotiation -> police warning/fine -> appropriate escalation). A transaction adapter debits V's actual eddies only after a verified accepted game interaction and applies an idempotent counterpart credit in simulation; validate game money APIs before implementation. Police nonviolent approach and fine/dialogue mechanics need isolated REDengine proofs; never assume stock NCPD AI performs legal citations or arrests. Record offers, payments, rejected demands, grievance effects and duplicate-payment protection in the event journal.

## Bribery and police integrity
PoliceNPC profile extends persistent social/economic records with duty status, integrity, corruption propensity, rank, career risk and trusted contacts. IncidentCase offers a BribeAttempt command with amount, actor IDs, context, corroborating witnesses and evidence persistence. A reproducible decision evaluation yields accepted/refused/escalated and reasons; money transfer uses the same idempotent game-wallet adapter and simulated ledger. Bribe acceptance only changes records/heat the recipient officer can plausibly influence; authoritative game wanted-level and NCPD behavior hooks require verification. Expose full decision traces, officer risk and case persistence in debugger.
