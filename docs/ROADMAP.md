# Roadmap (not started)

## Phase 0 — Integration proofs
- [ ] Confirm player platform, game version, framework versions and mod compatibility.
- [ ] Probe engine events for combat, hit zones, defeat, lethal/nonlethal outcomes, NPC lifetime.
- [ ] Demonstrate safe spawn/despawn, retreat task feasibility and save/reload persistent NPC ID.
- [ ] Probe vendor pricing and Kiroshi scanner UI integration.
- [ ] Document third-party dependencies/licensing and save/quest safety.

## Phase 1 — Deterministic simulation
- [ ] Core data schemas, migration and persistent event log.
- [ ] Faction relations, player reputation, reputation propagation via known information.
- [ ] Social graph, named NPC memories, intel provenance and expiration.
- [ ] Unit tests with fixed seeds, reload and idempotency.

## Phase 2 — Survival encounters
- [ ] Bounded local encounter scheduler with cleanup and quest guards.
- [ ] Morale, surrender, retreat, reinforcement and optional cyberware escapes.
- [ ] Injuries, rescue behavior, recovery and prosthetic changes.

## Phase 3 — Living Night City
- [ ] Territory control, strategic faction tick, resources, hierarchy and succession.
- [ ] Gang fights, raids, convoys and police/corporate response.
- [ ] Nemesis encounters, recognition, grudges and hunting.

## Phase 4 — Intel, clinics and economy
- [ ] Hacking, witnesses, informants, source confidence and counter-detection.
- [ ] Interconnected intel leads from gang NPC to shipment to hidden illegal ripperdoc.
- [ ] Independent/faction/corporate/illicit medical care and vendors.
- [ ] Faction-specific cyberware, upgrades, price tiers, availability, underground rare prototypes.
- [ ] Underworld dossier + scanner integration.
- [ ] Dynamic mod quests and faction lockouts; protect vanilla main quests.

## First playable scenario
V fights a gang; a named NPC survives and retreats; wounds and faction standing persist across reload; the survivor remembers V and reappears. Subsequently: shipment intel clue and a faction merchant pricing prototype.

## Definition of done
Repeatable in-game checks, targeted tests, quest safeguards, reload integrity, spawn cleanup, performance limits, logs, compatibility notes.

## Platform and release decision
Windows is the exclusive initial gameplay-development and validation target. First achieve a stable, playable Windows version; investigate native macOS support and adapters only afterward as a separate compatibility milestone. Architecture should preserve portability without blocking Windows progress.

### Later milestone: macOS investigation (deferred)
- [ ] Inventory supported native macOS modding frameworks at that time.
- [ ] Identify Windows-only hooks and their portable replacements.
- [ ] Test equivalent save formats and features on a Mac build.
- [ ] Release a macOS port only after standalone in-game compatibility testing.

## Planned ambient-life milestone (after initial engine feasibility)
- [ ] Probe civilian vehicle stopping/boarding, seat and pedestrian path control.
- [ ] Prototype non-explicit adult street-worker / driver conversation with multiple outcomes.
- [ ] Prototype rare staged road-accident aftermath, exits, dialogue and departure.
- [ ] Add weighted escalations (discussion, fistfight, threats, flight, shots) and civilian survival consequences.
- [ ] Investigate NCPD arrival, separation, questioning and arrests; fall back gracefully if engine API is unavailable.
- [ ] Instrument incident triggers, probabilities, decision factors and cleanup in dashboard.
- [ ] Validate pedestrian/traffic flow, safe mission guards, performance, cooldowns and settings.

## Confirmed priority decision — Undercity only after core stabilization (2026-10-23)
- First implement, tune and validate the gameplay mechanics and systemic simulation in the existing Night City world.
- Expect multiple cycles of in-game playtesting, balancing, performance profiling, bug fixes, save/load verification and compatibility work.
- Do not start new map or level construction while foundational gameplay systems remain unverified or unstable.
- **Final optional expansion milestone only:** investigate a modular Undercity (hidden clinics, underground markets, smuggling connections and later connected districts), beginning with a minimal room/nav/lighting proof of concept.
- The Undercity is explicitly not a dependency or release blocker for the first stable Windows mod.

## Street Cred and world reactivity
- [ ] Probe safe read access to vanilla Street Cred and changes over time.
- [ ] Separate fame, faction standing, actual NPC knowledge and personal relationships in simulation data.
- [ ] Prototype weak enemies recognizing notorious V, fleeing/calling reinforcements and elite faction pursuit.
- [ ] Add positive recognition from friendly factions and context-sensitive dialogue where supported.
- [ ] Add cooldowns, hunt limits, player intensity controls and dashboard decision logs; playtest for fun rather than constant punishment.

## Autonomous NPC investigations and hunt consequences
- [ ] Model HuntCase with motive, clues, budget, persistence, pursuit/abandonment conditions.
- [ ] Implement information gathering from witnesses, informants, territory contacts and optional netrunning.
- [ ] Resolve offscreen investigation risks (conflict with allies/rivals, injury, arrest, wasted resources) deterministically.
- [ ] Add hunter reassessment: continue, escalate, pause, negotiate or give up based on costs and personality.
- [ ] Surface known hunts and causal traces in developer dashboard and contextual gameplay hints.
- [ ] Add anti-omniscience, cooldown, player counterplay and protected-quest tests.

## NPC social network, finances and adaptive tactics
- [ ] Add typed family, friendship, alliance, obligation and hostility links across NPCs and factions.
- [ ] Model grudges/loyalties spreading from witnessed or learned injuries, betrayals and deaths.
- [ ] Create persistent NPC and faction budgets, income streams, expenses, debts and auditable transactions.
- [ ] Gate weapons, cyberware, medical recovery and recruitment by finances, supply and social connections.
- [ ] Make confrontation style depend on Street Cred, recognition, relative strength, courage, resources and motive.
- [ ] Simulate weak NPCs seeking support, ambushes or indirect retaliation and stronger NPCs preparing equipment or direct challenges.
- [ ] Cover economic conservation, relationship causality, power-creep limits, hunter cooldowns and replayable decision traces in tests/dashboard.

## Rank, lifestyle and clothing-driven social reactions
- [ ] Model promotions/demotions, salary and gang-income share by rank, authority and contacts.
- [ ] Add ordinary consumption, discretionary/luxury purchases, fashion, housing and debt alongside equipment and medical costs.
- [ ] Model clothing quality, style, condition, affiliations and perceived status separately from actual finances.
- [ ] Prototype V outfit-change effects on witness recognition while preserving facial/cyberware/personal recognition.
- [ ] Investigate stable dynamic NPC outfit changes and visual persistence across encounters.
- [ ] Test NPC reactions to perceived social standing, fashion and affiliations with anti-stereotyping and game balance constraints.

## Protected NPC and crowd promotion feasibility
- [ ] Catalogue protected vanilla/quest actors and safe read-only integration boundaries for ripperdocs/vendors.
- [ ] Verify visible crowd NPC attributes can be captured and recreated after despawn/load.
- [ ] Prototype one meaningful crowd encounter (collision, assault or rescue) promoting the actor into a stable simulated identity.
- [ ] Test generated minimal background and seeded, contradiction-free social links.
- [ ] Validate injured/nonlethal/dead outcomes and non-resurrection after reload.
- [ ] Simulate witnesses using crowd density, sightline, recognition uncertainty and dissemination delays.
- [ ] Verify consequences only reach relatives/friends/factions via learned reports; add replayable dashboard trace.
- [ ] Test bounded population growth, deduplication and save rollback.

## Civil consequences prototype
- [ ] Detect nonfatal vehicle collision, distinguish assault/death and gather credible witnesses.
- [ ] Prototype victim interaction and configurable medical/repair compensation request.
- [ ] Validate safe in-game eddies debit, transactional idempotency and NPC simulated credit.
- [ ] Test peaceful NCPD response, dialogue, warning/fine and escalation guards.
- [ ] Add negotiation/refusal/dispute/extortion distinctions, anti-spam cooldown and save/load tests.
- [ ] Explain liability, witness evidence, decisions and payments in the developer dashboard.

## NCPD bribery prototype
- [ ] Model officer integrity, financial incentives, rank, duty risk and witness/camera evidence.
- [ ] Prototype peaceful police encounter after nonfatal collision when V remains and complies.
- [ ] Offer optional bribe dialogue with accept, refuse, report and escalation results.
- [ ] Verify wallet deduction, officer credit, local heat effects, saved case state and reload idempotency.
- [ ] Test witness persistence, corruption contacts, blackmail and anti-spam fairness.
