# Local event roundtrip prototype

Implemented and unit-tested: a synchronous JSON-lines stdin/stdout adapter for the
Python simulation. This is a protocol/process proof, not a CET bridge or playable mod.
There is no network listener, game mutation, NPC spawn or background simulation.

## Run from the repository root

```powershell
python -m underworld.bridge --database world.sqlite3 --slot manual-test-save --timeline initial
```

Paste one JSON object per line (maximum 16 KiB including newline):

```json
{"protocol_version":1,"slot":"manual-test-save","timeline":"initial","event":{"event_id":"test-001","npc_id":"test-person","kind":"civilian_helped"}}
```

Response has status `applied`, reputation 15, protocol version and matching context.
Repeating the line returns `duplicate` and reputation remains 15. Restart with the
same database/context and repeat: still `duplicate`. A changed payload under the
same event ID is rejected. `civilian_harmed` is the other supported event kind.
Malformed, oversized, unsupported-version or mismatched-context messages return
`rejected` / `invalid_request` without changing state; the next line can be processed.
Database IO failures remain fatal and visible on stderr; never acknowledge an
uncommitted event. EOF closes the process. This adapter does not launch the game.

## Save boundaries and limitations

Slot and timeline must be supplied explicitly. A timeline identifies a particular
save-history branch; the bridge checks both against its startup context. Namespace
encoding prevents delimiter collisions. Existing prototype raw-slot records remain
preserved but are not automatically imported into a timeline. Database schema 0
upgrades to 1 without discarding records; newer schemas are rejected.

This does NOT detect actual game saves or restore a prior simulation checkpoint.
A new timeline starts empty; it does not inherit the old branch. Until a verified
save/load adapter and snapshot reconciliation exist, use disposable manual test
contexts only. Never connect this prototype automatically to a real campaign.

## Next integration proof

1. Verify CET Lua execution with a unique log marker in the interactive Windows game.
2. Check current supported CET IO/lifecycle APIs from primary documentation before coding.
3. Build a bounded nonblocking game-side transport; never call blocking stdin IO on a game callback.
4. Send one synthetic, mod-owned event and show its acknowledgement. No vanilla NPC changes.
5. Test disconnect/restart and save-load reconciliation before real gameplay events.

Run `python -m unittest discover -s tests -v` for the core and bridge checks.
