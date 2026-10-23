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
