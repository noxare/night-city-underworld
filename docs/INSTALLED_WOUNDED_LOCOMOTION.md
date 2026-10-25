# Installed wounded-locomotion binding — 2026-10-25

The bounded installed-resource audit found and converted:
- base/gameplay/ai/behaviors/reactions/hit_reactions.behavior (12454 bytes;
  SHA256 d6bd7c95ee61eb771e05c46800e36e539c81fbe5f01219d3fdda1bec297c2a92).
- base/gameplay/ai/behaviors/status_effects/wounded_entry_se.behavior (5968 bytes;
  SHA256 c9f4d7527b36bed4ae3bc1c962a2ec406bf33de38ae3d76ff02ae5579cf4c829).
- base/gameplay/anim_graphs/humanoid.animgraph (1111010 bytes;
  SHA256 f85e27f39130212d1303d005cb02236b9dbb0e42c6976f01d9af674b2952d14a).

Audit https://github.com/noxare/night-city-underworld/actions/runs/40232599116
and metadata inspection https://github.com/noxare/night-city-underworld/actions/runs/40233146709 .

The installed hit_reactions state containing PainReactionTask references wounded_entry_se.
In the installed wounded entry, CheckCurrentWoundedState selects WoundedLeftLeg
or WoundedRightLeg, then the relevant StatusEffectActions entry selector and an
ApplyAnimWrappersOnWeapon task with wrapperName woundedLocomotion_l_leg/r_leg.
These are actual installed resource names, not guessed animation-style integers.

Public native task source applies:
AnimationControllerComponent.SetAnimWrapperWeightOnOwnerAndItems(owner,wrapper,1).
Its Deactivate is empty; resetting our own test wrappers is our responsibility.
Source: https://github.com/CDPR-Modding-Documentation/Cyberpunk-Scripts/blob/main/scripts/cyberpunk/ai/Tasks/aiApplyAnimWrappersOnWeaponTask.script

## Adapter package
The owned test clone now sets these exact native wrappers at movement/injury
transitions, clears them on treatment and before deletion, waits for attachment
and avoids simultaneous leg-wrapper blends (latest selected leg takes priority).
It retains injury effects during flee transitions and measures actual speed.
No ordinary scanned actors are modified. Actual visible gait, physical speed
and interaction with native AI remain a bundled in-game acceptance requirement.

## Provenance limitation
The CLI -gp game context emitted identical resources for multiple requested
archives. The manifest's archive field therefore records the requested command
context, not a verified physical containing archive. Installed file identity and
content hashes are established; exact physical archive precedence needs separate
index evidence. Original assets and full converted JSON stay local only.
