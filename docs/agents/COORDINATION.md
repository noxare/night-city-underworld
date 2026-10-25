# Agent coordination and milestone delivery

The coordinator owns the final outcome, integration and user communication.
Specialists are task-scoped collaborators, not autonomous permanent services.

| Work | Ownership | Required evidence |
| --- | --- | --- |
| Animation, injury gait, behavior graph, NPC/player movement | Animation specialist: docs/agents/ANIMATION_SPECIALIST.md | Complete native activation path, installed-version evidence, cleanup and visible outcome |
| Deterministic simulation, injury rules, NPC state | Core task agent | Provenance, deterministic scenarios, no engine dependency |
| Bridge, SQLite, reload and identity | Persistence/integration task agent | Idempotency, context isolation, restart and rollback boundaries |
| Dashboard and diagnostics | UI/diagnostics task agent | Actual stored data, clear unknown/stale state, safe rendering |
| Verification and runtime delivery | Review/runtime task agent | Relevant tests, owned-process upgrade, installed files and heartbeat |

Use existing roles/playbooks before creating redundant ones. The animation role
is defined as a repository profile; other rows define assignment responsibilities,
not claims of already installed named agents. Assign concrete tasks only when
useful. Parallelize independent ownership; one owner per changed file. Integrate
dependent work sequentially and review every handoff.

## Conditional routing
- Unknown API/resource: animation/engine research, then installed-version probe.
- Database/IPC changes: persistence review before applying irreversible state.
- UI change: preserve engine capability/evidence labels; no invented success.
- Version/framework mismatch: crash-isolation playbook, one variation at a time.
- Worker failure: inspect owned process/log/heartbeat; do not kill arbitrary Python.
- Missing tool: discover existing exact path/version, inspect official CLI help;
  use a verified supported tool in an isolated audit folder if needed.
- Failed test: one targeted correction then reassess the cause; avoid blind retries.
- Missing visual proof: keep result unverified; bundle the required game acceptance.
- Quota/model limit: save exact commit/status/test evidence and a resumable next
  task. Use only actually available workers/models; no imaginary fallback.
- Session interruption: resume from repository state, not stale chat assumptions.

## Model policy
Small available models handle bounded indexing, summaries and routine tests.
Experts handle engine behavior, graph interpretation, architecture, persistence
and final review. Record actual use; do not claim transparent switching of the
current main model. Do not spawn all agents for every task.

## Handoff contract
Objective, owned files, base commit, findings and exact sources/versions, changes,
tests and runtime evidence, remaining blockers, next executable action. Preserve
other agents' changes. The coordinator persists meaningful progress in
docs/DEVELOPMENT_STATUS.md and does not end merely because a draft PR exists.

## Acceptance and honesty
Work through implementation, scoped tests, review, merge and reversible deployment
within existing authorization. Ask the user only for a coherent milestone test
or a concrete blocker requiring them. Never claim tests ran after the active
turn ends, a background agent will work forever, or a capability is verified
merely because a record/API exists.
