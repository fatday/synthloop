---
name: sl-repair
description: Diagnose and repair synthloop generator findings. Use when asked to fix reviewed defects, add ratchet tests, patch prompts/code/constants without shedding, or run the Claude repair workflow.
---

# Synthloop Repair

Diagnose first, then patch monotonically.

1. Read `CLAUDE.md`, `playbook/principles.md`,
   `playbook/03_quality_loop.md` section 3.4, `data_projects/ENVIRONMENT.md`,
   and the project's `progress.md`, `project_memory.md`, latest review, and
   relevant review instructions.
2. For each surviving finding, write the root cause before editing.
3. Apply the smallest generator/raw-quality fix that addresses the root cause.
4. Add a ratchet test or deterministic check for every confirmed incident.
   For code fixes, the new test must fail on the parent and pass on the fix.
5. Never autonomously net-tighten acceptance, relax a judge/rubric, weaken a
   ratchet, narrow coverage, or move a frozen baseline. Propose and stop for
   those.
6. Verify locally with the relevant tests/checks and, where possible, replay on
   prior rows.
7. Update `progress.md` and `project_memory.md` with diagnosis, fix, tests,
   remaining risk, and the next action.

A cycle that edited code cannot pass on the old batch; validate on a fresh
same-commit batch.
