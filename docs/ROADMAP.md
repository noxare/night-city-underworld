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
