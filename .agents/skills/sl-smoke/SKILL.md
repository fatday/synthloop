---
name: sl-smoke
description: Run synthloop small-scale generation. Use when asked to smoke-test a generator, generate a small batch, tally coverage, inspect raw rows, or run the Claude smoke workflow.
---

# Synthloop Smoke

Run the small-scale generation stage for one generator.

1. Read `CLAUDE.md`, `playbook/principles.md`, `playbook/03_quality_loop.md`
   section 3.1, `data_projects/ENVIRONMENT.md`, and the project's
   `progress.md` and `project_memory.md`.
2. Confirm the project is through implementation/design approval and has a
   runnable smoke spec or clear launch command.
3. Commit generator code before launch, or stop and explain why provenance is
   not satisfied.
4. Launch the pinned small batch exactly as recorded for the project. Do not
   improvise a new smoke config unless the human changes it.
5. Run coverage tally and deterministic checks required by the project.
6. Read stratified raw rows, oversampling failures, refusals, and weak cohorts.
7. Update `progress.md` with batch id/output path, commit, coverage, raw-row
   notes, verdict, and the single next action.

Do not mark the smoke complete if rows are missing, provenance is unclear, or a
designed capability has zero usage.
