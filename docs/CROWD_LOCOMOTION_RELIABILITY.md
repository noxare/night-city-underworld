# Crowd locomotion reliability follow-up

User observation (2026-10-25): several owned crowd clones were tested; only one showed the requested injury animation. Healthy flight did not run. This is partial visual evidence, not general compatibility.

The adapter now reads command activity with the native active-command list and reports no measured movement after three seconds. It records the source record, separates wrapper errors from movement measurement and binds the injury wrapper once after command activation (activation timing hypothesis, not a proven root cause). Cleanup clears stale measurements. Tests cover delayed activation/rebinding, no per-frame forcing and active commands with no movement.

Healthy MoveTo Run remains requested; no Walk fallback or forced follower role is introduced. Crowd AI role, navigation and per-record graph support remain under investigation. No successful healthy flight or reliable multi-record limp is claimed.

Primary API example: https://github.com/WolvenKit/cet-examples/blob/main/ai-components/AIControl.lua (IsCommandActive). Installed graph wrapper evidence: INSTALLED_WOUNDED_LOCOMOTION.md.
