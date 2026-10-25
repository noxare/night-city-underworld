# Animation specialist: initial engineering brief

## Diagnosis
The current Crowd clone + CrippledLeg + independent MoveTo experiment has not
verified injured locomotion. It also does not prove the animation is absent.
Investigate the actor-specific behavior-to-animation route before adding further
movement flags.

## Evidence
- The behavior documentation links hit_reactions.behavior state 5 to
  wounded_entry_se.behavior and PainReactionTask, with an injured-arm walking
  example. This is not proof of an injured-leg escape path.
- Public aiHitReactionTasks.script is v2.11. It obtains a hit-reaction proxy,
  sets upper-body state and initializes reaction features. Crowd activation
  stops traffic movement and clears fear. Deactivation restores state and stops
  the action. PainReactionTask is transient (~2.2 seconds). These are concrete
  older-source leads, not confirmed installed-2.5 behavior.
- Actor .ent animation components reference rig, animation sets and graph.
  The human animation graph and locomotion animation sets must be followed from
  the actual selected actor, not guessed from a cinematic clip.
- Codeware AnimFeature_Locomotion exposes action/style/speedProgress and playback
  fields but does not document a numeric limp selector. Do not guess style values.
- Player state machines/first- and third-person setup remain separate from NPC
  adapters. Scene/workspot clips are not automatically navmesh-compatible gait.

## Next internal implementation package
1. Audit installed game/framework/WolvenKit versions and supported CLI commands.
2. Locate actual 2.5 behavior resources, relevant .ent, humanoid animation graph,
   locomotion .anims and their dependencies. Use narrow asset-browser/CLI searches,
   not whole-game extraction or edits to vanilla archives.
3. Trace trigger -> actor eligibility -> behavior task -> graph parameters ->
   clip -> exit/cleanup. Record precise paths, nodes and TweakDB conditions.
4. Select one suitable owned non-story, nonpersistent test archetype based on
   the required AI path. Keep crowd as a comparison, not the only archetype.
5. Implement injured-walk and injured-escape intents using the same injury state;
   vary supported speed envelope, preserving gait. Use transitions, not per-frame
   animation reapplication.
6. Internally verify ownership, resources, interruption, second commands, effect
   removal, unload, reload, cleanup and displacement/speed evidence.
7. Deliver one bundled user acceptance: healthy -> injured walk -> injured escape
   -> interrupt/resume -> treatment -> cleanup. Freezing, sliding, normal gait
   during injury or injury loss during escape fail acceptance.

## Inspection workflow
WolvenKit Asset Browser opens individual archive assets. Dependency searches
("Find used files" / "Find files using this") require its Resources plugin.
For CLI first inspect installed help: use narrowly filtered unbundle and convert
for readable inspection; do not assume old cr2w command support.
Work in a separate audit directory; do not commit game assets to the repository.

## Concrete blocker
Installed 2.5 behavior/animation assets have not yet been traced to an injured
gait and suitable actor type. Asset inspection is the next productive internal
action. No further user micro-test is required to identify these resources.

## Primary source references
- https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/for-mod-creators-theory/files-and-what-they-do/file-formats/behaviors-.behavior-files.md
- https://github.com/CDPR-Modding-Documentation/Cyberpunk-Scripts/blob/main/scripts/cyberpunk/ai/Tasks/ReactionTasks/aiHitReactionTasks.script
- https://github.com/psiberx/cp2077-codeware/blob/main/scripts/Base/Imports/AnimFeature_Locomotion.reds
- https://wiki.redmodding.org/cyberpunk-2077-modding/modding-guides/animations
- https://wiki.redmodding.org/wolvenkit/wolvenkit-app/editor/asset-browser
- https://wiki.redmodding.org/wolvenkit/wolvenkit-app/usage/wolvenkit-search-finding-files
- https://wiki.redmodding.org/wolvenkit/wolvenkit-cli/usage/command-list
