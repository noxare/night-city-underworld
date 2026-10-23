# Phase 0 – Local simulation vertical slice

Initial **code prototype**, not yet a Cyberpunk mod or live REDengine integration.

- Pure Python evaluation accepts `civilian_helped` / `civilian_harmed` with stable `event_id` and `npc_id`.
- SQLite event journal stores separate save slots, suppresses duplicate event IDs within each slot, and survives process restart.
- Tests run on the self-hosted Windows runner, using `python -m unittest discover -s tests -v`.
- Deliberately no network server, Docker, CET injection, game process control, or changes to Cyberpunk files.
- Next: CET Lua bridge observes one **verified** gameplay event, sends a small serialized record through a minimal local IPC adapter; verify real event capture, save association, load rollback, and safe failure when the service is not running.
- Current reputation is an illustrative NPC-local score, **not yet** the agreed gang reputation, recognition or player Street Cred.
