---
name: smoke
description: Run a small-scale generation batch for a generator project, with provenance, coverage tally, and a first-pass raw-row read. Usage - /smoke <generator-name> [batch-size]
---

# /smoke <generator-name> [batch-size]

1. Read `data_projects/<name>/progress.md` and `design_spec.md`. Requires stage
   2-implement complete or later.
2. **Smoke spec — ask once, then never.** Look for a pinned **Smoke spec** in
   `progress.md`. If NONE exists, this is the ONE time you ask: elicit it from
   the human — which generators, batch size, model, time-box, nodes per
   generator, max-model-len, bring-up order — and pin it under `## Smoke spec`.
   If one EXISTS, use it verbatim and do NOT ask again unless the human says
   they want to change it. Either way, before any launch **echo the resolved
   config and assert it equals the pinned spec; on ANY mismatch (size, time,
   node count, which generators) STOP and surface it** — never silently
   improvise a different config.
3. **Provenance**: ensure the code that produced the batch is traceable — a WIP
   commit (record the hash), or, if the human owns commits, record the
   working-tree branch/state in the ledger instead.
4. **Pre-launch preflight (offline, seconds), in the venv that will run the
   job.** A green unit suite is NOT a launch check: it runs in the dev
   environment, on the dev's import path, and it does not build the engine.
   Keep a `scripts/preflight.py` in the project and run it before every
   `sbatch`. It must walk the WHOLE chain the launch touches and exit non-zero:
   every runtime module imports · the generator manifest resolves each arm ·
   every state's registered handler binds the runner's call shape · the first
   prompt builds · **the ENGINE the recipe names is constructed** · a real tool
   call dispatches.
5. Launch the smoke exactly as the pinned spec dictates. (Sizing guidance,
   relevant ONLY while first establishing the spec: a first-ever smoke can start
   tiny — 20-50 — to catch crashes cheaply, then the real size that lets the
   coverage spec register every capability. Once pinned, the spec governs.)
   **Arm the watch on failure signatures, not just terminal state**: ~10 min
   into the wall, compare the death/exception count against the previous
   batch's whole-wall count; if it is already higher, read the top reason and
   cancel — a terminal-state-only monitor is silent through a 100% crashloop.
6. While it runs, prepare the QA harness: confirm the **Track A post-data sweep**
   (`playbook/03_quality_loop.md` §3.2) is runnable over the landed batch. If the
   project has no sweep script yet, build one (`scripts/track_a_checks.py`):
   read-only, parses each row from itself, structural invariants HARD FAIL,
   quality signals reported-not-gated. Reuse/extend it every batch — each
   confirmed incident adds a check.
7. When rows land: run the Track A sweep immediately over the whole batch. HARD
   FAIL on any structural invariant (zero-usage capability, unparseable call,
   unadvertised tool, missing required arg). Read the quality signals — they
   often confirm/refute a fix before Track B spends tokens. Compare accept-rate
   to the previous batch.
8. Do a quick Track C read yourself: 10-20 stratified raw rows. Note anything
   that "feels off" even if no rule fires - those notes seed the review.
9. Append the batch to the ledger in `progress.md` (id, provenance, size,
   first-pass verdict). Report results and either proceed to `/review` or
   surface blockers.
