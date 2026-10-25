# Owned NPC injury-aware flight experiment

The test module now separates movement intent (walk/flee) from its requested leg-effect state. Flight targets a point 10 m away from the player, uses navigation, cancels the previous owned movement command, and reapplies requested native leg effects after command changes. Healthy flight requests Run; injured flight conservatively requests Walk and explicitly labels this as a fallback, NOT verified limping. Treatment/removal rebuilds the active movement command from the remaining injury flags. No vanilla actors or autonomous crowd flight behavior are overridden.

A new `Flucht vom Spieler testen` button enables a controlled healthy/injured comparison. The Lua test covers Run->injury->Walk, a repeated flee command retaining the injury/effect, recovery->Run, actor ownership and cleanup. The game may not honor a movement command or native effect as expected; those outcomes are not proved by a mocked test.

Open requirement: an actual native injured flee locomotion must be verified on Cyberpunk2.5. Slow Walk is not a substitute for the required persistent limping gait. This experiment does not satisfy that visual acceptance criterion yet.
