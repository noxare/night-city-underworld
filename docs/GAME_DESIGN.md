# Game design — Living specification

All features below are planned and subject to engine feasibility tests.

## World and faction relationships
Every gang (and relevant police/corporate organizations) pursues its own priorities, maintains relationships, controls territory and remembers crimes, support and betrayal. Actions for one group can reduce standing with opposing groups, according to actual interests and who learns of the action. Hostile reputation may trigger targeted searches and ambushes, suspicion, refusal to trade and exclusion from new faction jobs; player may negotiate restoration. Main story progression remains protected. A player's gang standing is not automatically public knowledge.

## Gangs and NPC social graph
Individual key NPCs get durable identities, hierarchy (boss / lieutenant / captain / member), loyalty, ambition, morale, contacts, friendships, rivalries and motives. A survivor may recognize V, retaliate, be promoted, seize leadership or move to a different gang. Death leaves consequences; an ally may rescue an injured NPC, while a disloyal boss can sacrifice subordinates.

## Fight, flight and recovery
Not all hostiles fight until death. Depending on personality, health, numbers, morale, terrain and cyberware, enemies can surrender, retreat, cover a friend's escape, seek reinforcements or flee. Advanced leg implants, Sandevistan or netrunning may aid escape where engine navigation/abilities allow. Nonlethal defeats matter. Record credible hit-zone trauma for head/torso/arms/legs, recovery over in-game time, loss of function, prosthetic replacement and differing access to medical care. Future meetings should reflect injuries, implants and memories.

## Gang conflict, police and simulations
Dynamic skirmishes on open streets, neighborhood influence changes, gang raids, patrols, convoy attacks, police and security interventions. Distant conflicts resolve in simulation; local conflict materializes within controlled budgets and quest safety restrictions. Witnesses or escalating violence raise police attention. NetWatch focuses on dangerous networking/Blackwall matters rather than every illegal implant.

## Cyberware identity and playstyle
Illustrative specializations, subject to lore refinement: Maelstrom—radical body modification, Tyger Claws—reflexes/blades, Animals—strength/durability, Voodoo Boys—netrunning, Valentinos—precision, 6th Street—military/tactics. Reputation can unlock discounts, specialized augmentations, upgrades and faction contacts. Gear may also be acquired through smuggling, theft, quests or black market so builds are not permanently class-locked. Experimental augments have tradeoffs, risk and quality rather than unconditional best-in-slot.

## Ripperdocs and faction economy
Four vendor types: neutral/independent; gang-affiliated; corporate; underground illegal. Reputation, personal trust, affiliation and scarcity affect service, discounts, markups, wares and treatment. Illegal ripperdocs occupy discoverable hideouts, may relocate after raids, can carry stolen/experimental restricted cyberware at high prices. NPCs also use clinics for recovery and upgrades. Prototype access may require components, rescued experts, delivery interdiction or intel rather than just money.

## Intelligence is gameplay
Basic Kiroshi scan shows visible/public traits, advanced scan offers selected details, intrusion/hacking may reveal hidden identities, loyalties, history, wound status, relationships, routes and plans. Hacking can be detected and traced. Intel has a source, recipient, reliability, freshness and secrecy; targets do not know everything. An underworld dossier connects known people, shipments, gangs, clinics and events. Old leads can become stale if a ripperdoc relocates.

### Example emergent chain (not a mandatory scripted quest)
V interrogates, scans or hacks a gang member -> obtains partial intel about illicit cyberware delivery -> locates/tracks/intercepts or protects the shipment -> finds a manifest revealing a hidden ripperdoc, supplier and buyer -> chooses whether to steal, resell, collaborate or expose. The shipment exists as part of the economy whether or not V intervenes. Losing it changes stock, finances, and future responses.

## Suggested reputation bands (provisional balancing)
- -100..-60 hostile: refuse some services / actively hunt.
- -59..-20 suspicious: possible markups / restricted inventory.
- -19..+19 neutral.
- +20..+49: illustrative 5% discount.
- +50..+79: illustrative 10% discount and specialist stock.
- +80..+100: illustrative 20% discount and rarities.
Numbers are proposals, not shipped values.

## Design safeguards
No perpetual ambush spam, impossible-to-escape bounty loops or softlocked vanilla quests. Intelligible consequences, player recovery options, world consistency, and performance-first encounter scheduling.

## Criminal economy and ambient adult nightlife (proposed)
- Fictional bank heists, armored transport robberies, warehouse raids, racketeering and gang-planned criminal operations with abstract planning, security response, consequences, witnesses and discoverable intelligence.
- Fictional illicit drug distribution networks: dealers, customers, couriers, supply disruptions, territorial competition and police intervention. Avoid real-world manufacturing or trafficking instructions.
- Adult-only street sex work and nightlife in suitable districts: social routines, contacts, safety, agency, protection/extortion tensions and non-explicit presentation. No sexual violence gameplay or minors.
- These activities share resources, faction reputation, intelligence, logistics, law-enforcement heat, territory and NPC survival systems. Prioritize atmosphere, choice and systemic consequences over graphic depictions.
- Treat all additions as design proposals; game engine feasibility and content compatibility require testing.

## Ambient life and emergent street incidents (planned, engine feasibility unknown)
Night City must feel alive outside player-centric combat. Introduce a **Civilian Life & Street Events** director that uses rare contextual ambient encounters rather than perpetual scripted chaos.

### Adult street-worker and client interactions (non-explicit)
- Adult street-based sex workers can wait, converse with occupants of arriving civilian vehicles, decline/accept an interaction, and optionally board a vehicle that departs. Others remain, change locations, talk among themselves, or leave after a shift.
- Behavior uses appropriate neighborhoods, schedules, valid vehicle stopping spaces, pedestrian paths, door/seat availability, animations and safety checks. Avoid any sexual depiction, coercive scripting, minors, or objectifying presentation; NPCs retain agency and everyday lives.
- Conversations should have distinct outcomes (short exchange, disagreement, refusal, agreement, departure), not automatically result in boarding. Make activity believable but non-explicit.

### Rare traffic accidents and social escalation
- Context-aware low-frequency road incidents. Where actual vehicle collisions cannot be safely orchestrated, use a validated staged aftermath with believable positions and traffic management.
- After an accident, occupants assess injury and temperament, may exit safely, exchange words or argue, exchange details, return to vehicles and leave, call assistance, start a fistfight, threaten with a weapon, flee, fire, or seek cover. Not every accident is a crime; most end peacefully.
- Escalations account for personality, existing faction ties, injury, witnesses, social stress and weapons. Multiple branches: one intimidates and the other flees; reciprocal threats; injury; surrender; police separation/arrest when supported.
- NCPD response includes dispatch, approach, de-escalation, aid, questioning and arrest where engine hooks allow. Avoid assuming generic vanilla police AI supports arrests; prototypes must establish feasibility and scripted alternatives.
- Despawn and cleanup safely outside player's awareness; handle vehicle obstruction, traffic AI, player interference, mission areas and non-duplicated persistent effects.

### Director fairness and observability
- Event probabilities, per-zone/day quotas, cooldowns, proximity rules, scene slots, global CPU/NPC/vehicle budgets, deterministic seeded event selection and debug traces.
- Rare incidents should not create constant roadblocks or combat. Provide player settings for event frequency and a disable toggle.
- Publish causal reasoning (event trigger, eligibility, NPC reactions, police dispatch, cleanup) to the underworld debug event journal/dashboard.

## Street Cred, recognition and calibrated threat response (decision 2026-10-23)
Separate **vanilla Street Cred (overall fame)** from **faction reputation (standing)**, **personal NPC memory**, and **knowledge propagation**. A highly famous V is not automatically identified by every pedestrian: recognition varies by faction intelligence, witnesses, disguise, district and context.

- At low Street Cred: strangers may underestimate V; ordinary encounters and baseline reinforcements apply.
- With growing fame: opponents may recognize V, comment, retreat, negotiate, seek cover, call allies or report sightings instead of automatically fighting to the death.
- Weak opponents against a notorious and demonstrably dangerous V should increasingly choose escape, surrender or **request plausible reinforcement**. Higher-ranking gangs may dispatch better-equipped response teams or recurring nemesis hunters if faction standing is hostile and V has been identified.
- Famous V with good standing should receive friendly recognition, cautious respect, help or reputation-specific dialogue—not just more ambushes.
- Street Cred is a modifier, not a hardcoded punishment: faction hostility, NPC courage, witness knowledge, territory strength, recent incidents and current quest context govern the actual behavior.
- Anti-frustration rules: cooldowns, regional encounter budgets, limits on active hunters, safe periods after major engagements, avoid unavoidable spawns/instant recognition and protect missions. Provide customizable encounter intensity and debug explanations.
- Use vanilla Street Cred value through a verified engine hook; never assume the exact API until tested. Cache/snapshot changes and ensure compatibility with the game's normal leveling and balance.

## Autonomous NPC investigations and manhunts (decision 2026-10-23)
A hostile NPC or faction does not magically know V's location. Hunters proactively investigate through their own imperfect intelligence networks: questioning contacts and witnesses, investigating last sightings, paying informants, intercepting gang chatter, searching known locations, or hacking when their skills permit. Clues carry confidence, freshness and provenance; hunters may pursue false/outdated leads.

Investigations have gameplay consequences for the hunters, even when V does not witness them: local arguments, damaged relationships with allies or informants, trespassing into rival territory, brawls, gunfire, injury, arrest, loss of resources and trust, or disappearance. Preserve plausible offscreen simulation rather than spawning all actions physically.

NPC personalities, rank, courage, loyalty, obsession, injuries, losses, counterpressure and available resources change their choices. A hunter may pause, negotiate, demand more support, abandon the vendetta, change allegiance, or turn against an overbearing superior. A determined Nemesis may return later with better intelligence.

The hunt must be fair: no omniscient tracking or instant teleporting, no chain attacks without cooldowns, no unavoidable pursuit during guarded quests. V can evade detection, misdirect leads, intimidate or reconcile. Offer ambient hints and dossier entries for discoverable investigations. Ensure a hunt has a traceable cause and possible conclusion.

## Social ties, personal grudges and NPC wealth (decision 2026-10-23)
- NPCs can have persistent family ties (parent, sibling, partner, other relatives), friendships, rivalries, personal debts, loyalties and enmities independently of gang affiliation. These ties can cross faction boundaries.
- Significant events affecting one NPC can propagate to relatives, friends, witnesses and allies as **information**. A bereaved friend may blame V or another NPC/gang; evidence, misinformation, personality and loyalties affect whether blame becomes a grudge or revenge. No omniscient knowledge.
- Reputation/Street Cred is a fame signal, distinct from faction standing, personal grievances and identification confidence. Weak opponents who recognize a formidable V tend toward retreat, recruiting support, stealthy sabotage or indirect retaliation rather than frontal confrontation. Powerful, confident or well-equipped rivals may challenge V openly, or deliberately prepare by obtaining stronger weapons/cyberware. Both can misjudge risks.
- Each persistent important NPC has a limited personal economy: cash/liquidity, income streams, obligations, debt, owned equipment, medical expenses, spending preferences and access to faction support. Factions have budgets and stock separate from personal NPC funds.
- Activities such as jobs, wages, trading, crime and loot may generate income; injuries, bribes, failed operations, maintenance, rent and upgrades cost money. Resources are conserved and traced through transactions where practical. Gear upgrades require both available funds and believable suppliers/access; no free spontaneous high-tier equipment.
- Socioeconomic position shapes opportunities without mechanically stereotyping every poor or wealthy character. Wealth influences access to treatment, bribes, intelligence, safe houses, weapons and experimental augmentation.
- Characters can seek funding, loans, stolen equipment or gang sponsorship, potentially creating new debts, betrayals and rivalries. Offscreen economic updates must use bounded aggregated ticks; no full economy simulation for every passing pedestrian.
- Preserve gameplay balance: cap elite pursuers and upgrade rates, ensure player counterplay and cooldowns, prevent runaway wealth accumulation and NPC power inflation.

## Advancement, lifestyle, fashion and recognition (decision 2026-10-23)
- Persistent gang NPCs may gain or lose rank through success, loyalty, competence, leadership vacancies, politics, betrayal and faction outcomes. Promotion increases authority, access, contacts and possibly income/share of gang revenue, but does not automatically make the NPC a better fighter.
- NPC budgets include recurring necessities, housing, leisure, nightlife, fashion, vehicles, status goods, gifts and hobbies, not just weapons, treatment and revenge. Spending is personality- and class-dependent and creates social standing, debts and visible lifestyle changes.
- Clothing is a meaningful but imperfect social signal: condition, quality, style, conspicuousness and perceived gang/corporate affiliation affect intimidation, access, respect, suspicion, bargaining and NPC reactions. An affluent character may visibly spend on clothing and luxury, but not all rich NPCs dress expensively and not all well-dressed NPCs are rich.
- Outfits are distinct from personal identity and reputation. A full change of clothes can lower short-term visual recognition, especially from incomplete witness descriptions, but cannot erase knowledge based on facial features, body shape, voice, distinctive cyberware, prior close encounters, biometrics or tracking records. A costume is not magical invisibility.
- The same clothing signals apply to V and other NPCs. NPCs can update outfits after promotion, injury, wealth gains/losses or changing affiliations, respecting available assets, suitable attire and engine feasibility.
- Disguise consequences depend on observation distance, local norms, witness accuracy, security technology and prior intel. NPCs can be fooled, suspicious, or recognize someone despite changed attire. Clothing should allow creative roleplay without becoming mandatory micromanagement.

## Protected canon NPCs, crowd promotion and witnesses (decision 2026-10-23)
- Quest-critical and fixed named NPCs, including ripperdocs who may be quest-related, remain vanilla-owned. Use an explicit protected/allowlist integration policy: no replacement, despawn, injury rewriting, altered quest flags, schedule manipulation or hostile combat overrides without validated safe hooks. Optional faction-reputation-based vendor prices/stock/services may be applied only after proving quest compatibility and offering safe fallbacks.
- Crowd NPCs normally remain anonymous, transient engine actors. When V meaningfully interacts with a bystander (assault, vehicle collision, being shot, help, rescue, conversation with a lasting consequence), attempt to **promote** them to a persistent simulated character.
- Capture only verified reconstructible appearance attributes (character archetype/template, available outfit assets, facial/hair/visible cyberware descriptors, voice where accessible), scene location, time, injury state and event identifiers. Assign a separate stable Underworld ID; do not treat transient engine handles as persistence keys. If exact visual reproduction proves impossible, downgrade gracefully with a clear compatibility limit.
- Generate a coherent **initial background** (name, occupation, economic standing, plausible ties and contacts) from district and archetype, not an omniscient prewritten life. Use a seeded generator for reproducibility and avoid retroactive contradictions with already-observed behavior. Sparse background can expand on demand; do not create full genealogies for every crowd actor.
- Physical outcomes distinguish injury, nonlethal incapacitation, death, escape and uncertain status. Preserve causal links and do not resurrect NPCs who are confirmed killed.
- Witnesses are modeled explicitly. More plausible nearby witnesses increase the chance of the event being reported, but crowd density is not an automatic omniscient broadcast: sightline, proximity, attention, survival, reliability, fear, allegiances, time and whether V was identified are important.
- Witness reports may reach police, gangs, friends or family over time, create incomplete or mistaken identity leads, affect reputation, personal grudges, fear and future encounters. Relatives react only to information they learned, possibly through intermediaries. Reports can conflict or remain unresolved.
- Avoid automatically spawning relatives solely as retaliation; the social graph should allow reconciliation, mourning, investigation and independent choices.

## Civil compensation and proportionate police response (2026-10-23)
- Nonfatal collisions and minor assaults can lead to victim demands for medical expenses, repairs or compensation, rather than automatic combat. Liability should depend on evidence, injury, witnesses, fault and whether the victim recognizes V.
- Requests can be paid from V's in-game eddies balance, negotiated, disputed, ignored or handled through an authority/mediator. Distinguish legitimate compensation from attempted extortion or fraud.
- NCPD should ideally arrive peacefully for low-severity incidents, issue a fine or warning, gather statements and leave when the situation is resolved. Escalation to threats/arrest/combat is contextual (ongoing violence, drawn weapons, refusal, serious crimes), not automatic.
- Injured pedestrians can receive medical attention; victims and witnesses remember settlement or misconduct. Payment affects their personal financial ledger and potentially reduces grudges, but does not erase every social consequence.
- Avoid punitive spam or impossible-to-pay debt spirals: caps, cooldowns, graduated charges, optional accessibility settings and a reasonable opportunity to respond.

## NCPD corruption, bribes and voluntary compliance (decision 2026-10-23)
- When V causes a road collision involving a pedestrian and **remains on scene without threatening or resisting**, responding NCPD should prefer safe assessment, aid, witness interviews and dialogue where technically feasible; use severity-dependent consequences rather than automatic gunfire.
- V may attempt a discreet **bribe** as one resolution choice alongside lawful fine/compensation, negotiation and accepting consequences. Bribes are in-game fictional interaction, never guaranteed.
- Officer decisions depend on individual integrity/corruption, financial pressure, rank, fear of V, witness/camera presence, colleagues, crime severity and available evidence. Officers may accept, refuse, warn, arrest, demand more, report misconduct, or later extort V.
- If accepted, transfer money from V to an officer's simulated personal ledger, reduce or delay police attention only to the plausible extent of that officer's authority; independent witnesses, recorded evidence and other officers may keep the case alive. A fatality or egregious violence is harder to conceal than a minor collision.
- Bribery may create persistent social consequences: a corrupt contact, blackmail exposure, internal-affairs investigation, rival officers, gang information leaks, loss of officer's career, or a later request for a favor. Avoid endless automatic extortion; use cooldowns, risk limits and player counterplay.
- Preserve a nonviolent encounter path and avoid guaranteeing immunity or tying all police encounters to payments.

## Layered NCPD recognition and investigative heat (2026-10-23)
Keep vanilla 1–5 star police pursuit as the acute response to immediate dangerous behavior, with MaxTac at maximum heat. Add a **separate persistent investigative layer**, so lower-severity incidents can lead to warnings, fines, questioning and later recognition by patrolling officers rather than instant gunfire.
- Distinguish current active heat/stars, open incidents/cases, evidence quality, district warrants, confirmed/suspected identity, vehicle description and officer-local recognition.
- A patrol may notice a wanted vehicle, matching clothing, a clear facial description, or an identified V with an active local case; suspicious observations prompt checking/questioning where possible, not automatic shooting. A different outfit reduces confidence, but not prior biometric or personal knowledge.
- Escalation depends on severity, compliance, weapons shown, dangerous recent acts, violence, case evidence and officer temperament: observe -> talk -> warning/fine -> attempted detention -> tactical reinforcements -> active lethal pursuit -> MaxTac for extreme ongoing threats.
- Eyewitnesses, cameras and social reports accumulate credible evidence; anonymous sightings must not magically identify V. Local NCPD knowledge can spread between patrols, subject to communications/time and witness confidence.
- Escaping line of sight can clear active heat while unresolved cases remain investigable. Case expiry, settlement, corruption, bribes and legal-like dispute paths can change case state without wiping indisputable evidence.
- Preserve high-intensity police response to spree killings and severe violence; never allow cheap bribes or a quick clothing change to erase a major incident.
- Offer clear player feedback, low nuisance frequency, player counterplay, patrol recognition cooldowns and story-safe guards.
- Related third-party mod: NCPD Case Files models persistent investigations, patrol recognition and vehicle warrants. Review compatibility and permission before adopting ideas/code.

## Rare, ambient policing rather than routine player harassment (2026-10-23)
- Night City is large: routine checks of V should be **rare**, even with an open minor incident. A known case creates conditional recognition only when the right officer, location, evidence and circumstance converge, not a citywide stop-on-sight loop.
- Favor contextual ambient world events: patrol officers conversing with pedestrians, checking vehicles, responding to accidents, mediating disputes, questioning another NPC, processing minor offenses, or departing peacefully. Most occur independently of V.
- Use low base event probabilities, district and time-of-day weights, cooldowns and spawn/performance limits; keep police presence believable without transforming free roaming into constant interruptions. Serious active crimes remain an exception.
- Player agency: V may observe, intervene, walk past, help, evade or negotiate. Encounters must not force dialogue merely because V passes nearby.

## Contextual ambient micro-interactions (2026-10-23)
- Ambient encounters happen in the **player's surrounding world** and should preferentially reuse existing streamed NPCs rather than spawn artificial events directly in view.
- Nearby pedestrians may begin brief conversations naturally when sharing context: waiting at a crosswalk, sheltering from weather, queueing, watching an incident, sitting together, commuting or recognizing an acquaintance. Some interactions are mundane and don't concern V.
- Patrol officers can casually speak with pedestrians, give directions, check on wellbeing or discuss an incident without interrogating V.
- Initiation should require spatial proximity, compatible movement/idle states, a suitable stopping spot, no blocking of sidewalks or crossings, availability of dialogue/gestures and appropriate social context. Walk signals and traffic must continue to work.
- Short interactions may resolve through greetings, small talk, disagreement, laughter, refusal or simply walking away. Keep conversations sparse, varied, interruptible and not repetitive.
- Protect performance and quest flows. Participants gracefully return to their previous crowd behavior when dialogue ends, V leaves or danger appears. Do not commandeer quest-critical NPCs.
- A small fraction of encounters may create information or relationship changes, but most are just ambiance and do not require permanent character promotion.

## Major quest decisions as systemic socioeconomic shocks (2026-10-23)
- Add a World Consequence Director that consumes **verified canonical quest outcomes** and emits plausible, bounded economic and social shocks to affected factions, districts, companies, supply chains and individuals. These are mod-authored extrapolations, not claims of vanilla scripted outcomes.
- Dogtown / Phantom Liberty: after Hansen's fall, read the later Bennett/Jago succession outcome where available, rather than treating Dogtown as leaderless forever. Leadership, Barghest cohesion, Mr. Hands relationships and trade access drive security, smugglers, price volatility, employment, extortion, medical demand and living standards.
- Other illustrative choice hooks: Royce/Brick Maelstrom succession; Clouds/Maiko and Tyger Claws control; Voodoo Boys/NetWatch network stability; prominent gang or corporate outcomes. Only apply consequences to branches that actually occurred. No mutation of protected quest flags or essential actors.
- Model second-order effects: convoy disruption -> shortage -> clinic prices -> postponed NPC operation -> missed work -> lower household income -> increased debt -> possible new activity. Outcomes should be localized, gradually propagate over actual trade links and depend on stock, reserves, substitutes and recovery.
- District metrics: employment, wages, household purchasing power, security, faction power, market supply, prices, medical access, housing pressure, public sentiment and police legitimacy. Use aggregated populations for anonymous civilians; persistent character ledgers and relationships for significant NPCs.
- Player can profit, alleviate problems, investigate, invest, mediate or ignore. Consequences should offer **meaningful opportunities**, not endless punishment. Long-term recovery, adaptive NPC behavior and alternative suppliers avoid permanent collapsed regions.
- Major choice reconciliation: read-only quest snapshot and idempotent event IDs; never repeatedly reapply a one-time story shock on load. Save-slot isolation, temporal checks and careful protection of vanilla progression are mandatory.
- In-game observability: rumors, street dialogue, local news, shop stock/prices, changed NPC clothing/behavior, increased clinic queues, patrols and changing neighborhood life. Developer dashboard shows each shock, propagated effects and counterfactual scenario tests.

## Underworld wherever the simulation runs (decision 2026-10-23)
The player should experience the same persistent NPC relationships, economy, faction decisions and emergent world regardless of whether the Underworld simulation executes on their gaming PC, another computer, NAS or hosted server. Support offline/local-first play as the baseline. macOS game support is a future bridge-specific feasibility question, not a reason to fork simulation gameplay. Console support may be absent or reduced depending on officially permitted mod interfaces. Do not promise cross-platform parity until confirmed.

## Visible injury behavior and bundled NPC milestone (2026-10-25)

User requirement: deliver coherent playable feature bundles rather than asking the user to validate every implementation increment. Internal targeted tests and small auditable commits remain appropriate. The next NPC milestone should combine acquisition/identity inspection, an observed encounter, injury state, visible reaction where supported, persistence and dashboard evidence into one repeatable test scenario.

NPC injuries must have visible consequences, not just hidden numerical state:
- Immediate hit reactions appropriate to observed damage and supported animation facilities.
- Persistent leg injury: limping, reduced gait and suitable movement transitions where engine support is verified.
- Arm injury: protective posture and restricted weapon/arm use where supported.
- Torso injury: supported pain/protective posture and appropriate reduced activity.
- Severe injury: supported stagger, fall, nonlethal incapacitation, retreat or surrender; distinguish actual death.
- Recovery and later treatment/prosthetics update both injury rules and supported visible behavior.

These are requirements, not implemented or engine-verified features. Do not assume baseline game reactions are absent or adequate: record existing behavior first. Verify available hit-zone signals, animation resources, AI locomotion modes and transition hooks on the installed Windows version. Do not infer an injured limb from generic HP loss. Avoid forcing an animation every frame or overriding quest-critical actor behavior. Injuries must remain compatible with navigation, combat, streaming, interruption and cleanup; release interventions safely when actors unload or a scene ends.

Acceptance for the bundled milestone:
1. Identify a suitable test actor; protect vanilla quest actors and establish an explicit supported actor scope.
2. Observe reliable damage/nonlethal/death and body-zone signals; show their provenance and unsupported capabilities in the dashboard.
3. Demonstrate at least one verified injury-to-visible-behavior transition (e.g. a leg injury and supported limp) without stuck AI or broken navigation.
4. Persist validated Underworld injury/encounter state with explicit save-context safeguards. Do not promise arbitrary crowd reconstruction before proving stable identity.
5. Verify interruption, actor cleanup, repeated damage, recovery and supported save/reload boundaries.
6. Deliver a compact end-to-end user test, with known limitations and measured in-game evidence. If the engine does not expose a required animation reliably, report the blocker rather than substituting a hidden modifier and calling the visual requirement complete.

## Injury gait must survive flight-state transitions (2026-10-25)

Binding user requirement: a leg-injured NPC must flee with an injured/limping gait.
Switching into flight, combat repositioning or another AI movement intent must not
silently restore normal running. Separate intent (escape destination/urgency) from
injury constraints (gait, posture and supported speed range). Resolve active injury
constraints after movement-intent changes and remove them only after explicit
recovery/treatment. Do not force an animation every frame or bypass navigation.

Acceptance must include a BEFORE injury baseline, injured walking, injured flight,
interruption/resumption and recovery. In particular, normal running during a
persistent leg injury fails acceptance even if an earlier idle pain reaction was
visible. A successful manual Walk command does not prove the flee integration.
This requirement is not yet verified in the live game adapter.


## Automatic promotion and simulation/materialization — confirmed 2026-10-26

A player shooting an eligible NPC automatically establishes a fixed Nemesis person and the causal memory "V injured me". Identify the actual hit actor and anatomical evidence; do not require manual spawn/limb/flee buttons. "Static" means durable personhood, not frozen locomotion. Do not treat an archetype record as an individual.

The physical body exists only where needed around V. Outside that scope, simulate position, injuries, intent and relationships. On reapproach, preload that SAME person before a visible encounter, with the SAME face, body, clothing and supported visual/equipment state. Store the concrete reconstruction data; no random substitute is acceptable. Preserve death, injuries and memory, protect quests and prevent duplicate bodies. Exact visual reconstruction and view-driven engine LOD are explicit capabilities to verify, not inferred from sharing a record.

Initial implementation and release gates: [AUTOMATIC_NEMESIS.md](AUTOMATIC_NEMESIS.md).
