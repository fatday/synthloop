---
name: sl-scale
description: Run synthloop scale-up and release workflow. Use when the human has explicitly approved scale-up, production launch, monitoring, release notes, or the Claude scale workflow.
---

# Synthloop Scale

Run stage 4 only after explicit human scale-up approval.

1. If the current thread does not contain explicit human approval to scale this
   generator, stop and ask for it.
2. Read `CLAUDE.md`, `playbook/principles.md`, `playbook/04_scale.md`,
   `data_projects/ENVIRONMENT.md`, and the project's `progress.md`,
   `project_memory.md`, latest passing review, and launch/runbook notes.
3. Complete preflight: committed code, provenance recorded, external reality
   checks turned into a watch plan, telemetry live on first shards, monitors
   armed, failure policy clear.
4. Launch exactly the approved scale plan. Track scheduler state, crash
   signatures, row counts, rates, coverage, and external-truth deltas.
5. Spot-read fresh rows during the run and after any hotfix.
6. Before release, run final QA and an at-scale stratified raw-row read.
7. Publish only on explicit human request, with batch metadata and caveats.
8. Write the postmortem and update `progress.md` and `project_memory.md`.

Do not scale, publish, or release on inference alone.
