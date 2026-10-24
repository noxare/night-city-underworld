# Night City: Underworld — Development rules

Read README.md and docs/{ARCHITECTURE,GAME_DESIGN,ROADMAP}.md before modifications.
Use docs/PLAYBOOKS.md for resume, model routing, crash diagnostics and handoff. Delegate bounded routine tasks to a smaller available model when supported; keep architecture, engine hooks, persistence/rollback and final review with the main model. Record actual model use and never claim an unverified local worker is available.
Do not claim any engine feature works without an in-game test; distinguish design, code and verified implementation.
Separate deterministic simulation from REDengine adapters. Use save schema versions and idempotent events.
Protect vanilla story-critical quests and actors. Apply strict spawn limits and cleanup.
Only run tests relevant to touched modules, expanding to full integration tests when justified.
Use small auditable changes/PRs and add tests, docs and reproducibility notes.
Respect CD PROJEKT RED fan-content policies, license compatibility and third-party assets; no unauthorized copying.

Platform policy: prioritize Windows x64 and a working Cyberpunk 2077 integration. Native macOS porting is deferred until the Windows mod is playable and stable. Keep core rules portable when practical but do not spend development time on speculative macOS engine adapters.
