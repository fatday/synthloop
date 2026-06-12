---
name: scale
description: Preflight, launch, monitor, and release a production-scale generation run for a generator project. Requires the stage-3 human gate. Usage - /scale <generator-name>
---

# /scale <generator-name>

1. Verify the stage-3 human gate is recorded in `progress.md` (two
   consecutive passing cycles + explicit approval). If not, STOP and say so.
2. Read `playbook/04_scale.md` and the design spec's External Reality
   Checks. Execute the preflight checklist verbatim:
   - commit + record hash; verify row/batch stamps carry it
   - instantiate the reality-check watch plan (sources, cadence, expected
     deltas)
   - arm monitoring: crash-signature log watch, scheduler-state watch
     (held/stuck jobs auto-remediation per the agreed failure policy),
     row-count deltas
3. Launch per the runbook. On the FIRST shards: verify every capability
   counter is moving as the coverage spec predicts. Zero usage on a designed
   capability blocks the run.
4. During the run: cadenced health passes (scheduler, crashes, row rates,
   fresh-shard coverage tallies, external-truth deltas). Follow the mid-run
   hotfix policy: commit first, record cutover timestamps, keep batches
   separable. Wake the human only for data-corrupting bugs or systemic
   stalls; log infra flakiness in the incident log instead.
5. After any production code change: spot-check fresh rows to confirm the
   change shows up in the DATA, not just the tests.
6. Release: final dual-track QA on the at-scale corpus, stratified raw read
   on at-scale rows, publish only on explicit human request, with batch
   metadata (counts, commits, window, caveats, mixed-generation split keys).
7. Postmortem into `project_memory.md` and, for process failures, update
   `playbook/` in the same change. Append the final ledger entry.
