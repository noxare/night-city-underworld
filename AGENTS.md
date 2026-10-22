# Night City: Underworld — Development rules

Read README.md and docs/{ARCHITECTURE,GAME_DESIGN,ROADMAP}.md before modifications.
Do not claim any engine feature works without an in-game test; distinguish design, code and verified implementation.
Separate deterministic simulation from REDengine adapters. Use save schema versions and idempotent events.
Protect vanilla story-critical quests and actors. Apply strict spawn limits and cleanup.
Only run tests relevant to touched modules, expanding to full integration tests when justified.
Use small auditable changes/PRs and add tests, docs and reproducibility notes.
Respect CD PROJEKT RED fan-content policies, license compatibility and third-party assets; no unauthorized copying.
