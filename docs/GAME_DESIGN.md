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
