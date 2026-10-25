# Injury engine integration evidence

The NPC package now probes native reaction samples separately from OnHit events.
It checks the installed CrippledLegLeft/CrippledLegRight records without applying
them. A successful observer registration is not proof the callback fires.

The source available in CDPR-Modding-Documentation/Cyberpunk-Scripts is version
2.11, not the installed 2.5. It describes reaction groups 1=head, 2=left chest/arm/
hand, 3=right chest/arm/hand, 4=abdomen, 5=left leg, 6=right leg. The probe retains
the raw group and simulation timestamp with that source-version caveat; it does
not convert ambiguous animation groups into authoritative limb injuries.

Sources: scripts/cyberpunk/NPC/components/hitReactionComponent.script and
scripts/cyberpunk/ai/Tasks/ReactionTasks/aiHitReactionTasks.script in
https://github.com/CDPR-Modding-Documentation/Cyberpunk-Scripts . Native wound
processing applies Crippled status effects and Pain reactions with exclusions.
This does not prove that a status effect alone provides persistent limping.

Still not delivered: a verified 2.5 body-zone adapter and a locomotion-compatible
animation controller restricted to mod-owned test actors with cleanup. Scanned
vanilla actors remain read-only. No animation, health or quest mutations are made.
The current injury reducer remains a simulation foundation, not an active gait
controller. These open requirements must not be labelled complete.
