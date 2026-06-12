---
name: smoke
description: Run a small-scale generation batch for a generator project, with provenance, coverage tally, and a first-pass raw-row read. Usage - /smoke <generator-name> [batch-size]
---

# /smoke <generator-name> [batch-size]

1. Read `data_projects/<name>/progress.md` and `design_spec.md`. Requires stage
   2-implement complete (runbook filled) or later.
2. **Provenance first**: ensure the generator codebase is committed (a WIP
   commit is fine). Record the commit hash.
3. Run the smoke per the runbook. Default size: enough for the coverage spec
   to register every capability (typically 500-5000; for a first-ever smoke,
   start at 20-50 to catch crashes cheaply, then go to the real size).
4. While it runs, prepare the QA harness: confirm the coverage tally and
   deterministic checks from `playbook/03_quality_loop.md` Track A are
   runnable.
5. When rows land: run Track A immediately. HARD FAIL on any designed
   capability at zero usage. Compare accept-rate to the previous batch.
6. Do a quick Track C read yourself: 10-20 stratified raw rows. Note anything
   that "feels off" even if no rule fires - those notes seed the review.
7. Append the batch to the ledger in `progress.md` (id, commit, size,
   first-pass verdict). Report results and either proceed to `/review` or
   surface blockers.
