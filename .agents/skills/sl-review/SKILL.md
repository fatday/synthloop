---
name: sl-review
description: Run synthloop dual-track QA. Use when asked to review generated data, run Track-A deterministic checks, Track-B agent review with refutation, raw-row read, verdicting, or the Claude review workflow.
---

# Synthloop Review

Review one generated batch with the full synthloop QA contract.

1. Read `CLAUDE.md`, `playbook/principles.md`,
   `playbook/03_quality_loop.md` section 3.2, `playbook/review_rubric.md`,
   `data_projects/ENVIRONMENT.md`, and the project's `progress.md`,
   `project_memory.md`, and latest `review_instructions/v*.md`.
2. Run Track A deterministic checks over the whole accepted batch.
3. Run Track B agent review on the pinned rubric, with a refutation pass before
   reporting findings.
4. Run Track C stratified raw-row read. Metrics passing is not evidence without
   raw rows.
5. Preserve full row ids and verbatim offending content for every surviving
   finding; do not truncate evidence.
6. Score pass/fail as a two-track AND: Track A and Track B must independently
   clear the target, worst cohort first.
7. Write or update the durable review summary expected by the project, then
   update `progress.md` with the verdict and next action.

Do not relax the rubric, weaken ratchets, or merge Track A and Track B into a
single blended score.
