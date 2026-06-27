---
name: sl-cycle
description: Run synthloop's autonomous quality loop. Use when asked to cycle a generator through smoke, review, repair, and repeat to the checkpoint, or run the Claude cycle workflow.
---

# Synthloop Cycle

Drive the inner loop for one generator until a pass checkpoint or hard stop.

1. Read `CLAUDE.md`, `playbook/principles.md`,
   `playbook/03_quality_loop.md` sections 3.1-3.5,
   `data_projects/ENVIRONMENT.md`, and the project's `progress.md`,
   `project_memory.md`, latest review instructions, and latest review summary.
2. Resume from the stage cursor in `progress.md` if one is active. Do not
   restart an in-flight smoke/review/repair unless the cursor says to.
3. Run smoke, review, and repair using the `sl-smoke`, `sl-review`, and
   `sl-repair` workflows.
4. Stop and present, never cross alone, on any hard gate: major design pivot,
   net-tightened acceptance, judge relaxation, weakened ratchet, coverage
   narrowing, scope expansion, oscillation, regression, infra failure, or
   safety cap.
5. A pass requires a clean cycle with no edits, both Track A and Track B meeting
   target independently, worst cohorts passing, coverage floors intact, drift
   within budget, and no new raw-row concerns.
6. Update `progress.md` at every sub-stage transition with the cursor,
   provenance, batch/review handles, stop reason, and one next action.

Never auto-scale or release. Hand back at the checkpoint for human review.
