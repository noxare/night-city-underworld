# Offscreen NPC simulation — first bounded core slice (2026-10-26)

This feature is a deterministic **simulation foundation only**. It neither promotes
vanilla NPCs nor creates persistent entities in Cyberpunk yet.

- `PersistentNPC` uses a durable mod-generated ID and an immutable
  `appearance_id` so a later verified spawn adapter can request the same appearance.
  The token alone does **not** establish that REDengine can reproduce the NPC.
- While visible, the simulator never moves the NPC. `leave_view` reconciles its
  last actually observed position, after which `simulate_to` updates it offscreen.
- Re-entry returns a **candidate** world position; no spawn occurs unless a future
  adapter proves save context, quest guards, navmesh, resource lifecycle, distance,
  caps and no-popping conditions.
- Straight-line travel is an intentionally abstract baseline, **not** navigation
  through Night City roads or buildings. Long gaps cap displacement to one hour.
- `speed_mps` is externally provided; injury/morale rules, route selection,
  persistent store integration and engine reconciliation remain to be implemented.
- Internal verification target: `python -m unittest tests.test_offscreen -v`.
  No live Windows or game test is claimed by this module.

Next: persist/replay the promoted identity with explicit game save/timeline
context, establish deterministic injury-dependent speeds, and then test
safe spawn/cleanup on owned NPCs only. Real NPC promotion must follow confirmed
hit evidence rather than a generic target-selection button.
