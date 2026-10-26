# Night City: Underworld — Development rules

Read README.md and docs/{ARCHITECTURE,GAME_DESIGN,ROADMAP}.md before modifications.
Use docs/PLAYBOOKS.md for resume, model routing, crash diagnostics and handoff. Delegate bounded routine tasks to a smaller available model when supported; keep architecture, engine hooks, persistence/rollback and final review with the main model. Record actual model use and never claim an unverified local worker is available.
Do not claim any engine feature works without an in-game test; distinguish design, code and verified implementation.
Separate deterministic simulation from REDengine adapters. Use save schema versions and idempotent events.
Protect vanilla story-critical quests and actors. Apply strict spawn limits and cleanup.
Only run tests relevant to touched modules, expanding to full integration tests when justified.
Use small auditable changes/PRs and add tests, docs and reproducibility notes.
User acceptance is milestone-based: complete coherent end-to-end feature bundles and internal tests before asking for an in-game check. Do not ask the user to test each implementation increment. Escalate only concrete blockers requiring user action. See docs/NPC_MILESTONE.md for the next bundled NPC/injury scope.
Animation/locomotion ownership: delegate animation, injury-gait, behavior-graph and player/NPC movement work to the animation specialist role in docs/agents/ANIMATION_SPECIALIST.md. Follow docs/playbooks/ANIMATION_LOCOMOTION.md, including complete engine-chain investigation, bundled internal verification and explicit in-game evidence. Do not substitute generic Walk/Run commands for a verified injured gait.
Use docs/agents/COORDINATION.md for conditional specialist routing, handoffs and milestone delivery. docs/PROJECT_CONTINUATION_PROMPT.md contains the reusable project continuation prompt.
Respect CD PROJEKT RED fan-content policies, license compatibility and third-party assets; no unauthorized copying.

Platform policy: prioritize Windows x64 and a working Cyberpunk 2077 integration. Native macOS porting is deferred until the Windows mod is playable and stable. Keep core rules portable when practical but do not spend development time on speculative macOS engine adapters.

Offline gaming-PC policy: an intentionally stopped Windows runner blocks only installation and installed/game validation. Continue independent repository implementation, scoped local tests and hosted core CI; do not repeatedly poll the runner or request gameplay micro-tests while the user is away. Preserve the pending deployment boundary explicitly.
