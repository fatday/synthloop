# Stage 4: Scale and Release

**Purpose**: run the approved generator at production scale, watch the things
that only break at scale, and release data with provenance. The loop does not
end at launch; it ends at a postmortem that updates the playbook.

## Preflight (before the launch command)

- [ ] Finish the exact launch_plan.json before asking for approval. Verify two
      consecutive clean validation passes on the same fingerprint with distinct
      seeds, ratified design deltas, and recorded design/scale authorizations.
      Existing plan-bound approval survives a new session; do not ask again
      solely because the approval was in another conversation.
- [ ] Run the shared `check-gates` command from runtime.md immediately before
      launch. Changed code, live inputs or plan invalidate the old check.
- [ ] Reserve an idempotency key and reconcile prior job state before submitting;
      bind live row/cost/time limits and bounded retries to the approved plan.
- [ ] Code committed; commit hash recorded in `progress.md` next to the
      launch entry. If rows carry a commit stamp, verify it is this commit.
- [ ] The design spec's External Reality Checks instantiated as a concrete
      watch plan: which dashboards/quotas get checked, at what cadence, with
      what expected deltas.
- [ ] Telemetry hooks verified by directed preflight cases. On the FIRST shards,
      check live counters against expected usage and minimum observation counts;
      pause for confirmed dark capabilities, not just undersized random samples.
- [ ] Monitoring armed: crash/fatal-signature watch on logs, scheduler-state
      watch (held/stuck/requeued jobs), row-count deltas at a regular cadence.
- [ ] Failure policy decided in advance: what gets auto-remediated (release a
      held job, restart a worker), what degrades gracefully (run at reduced
      workers), what wakes the human (data-corrupting bugs, systemic stalls).

## During the run

- Cadenced health passes: scheduler state, crash scan, row counts and rates,
  coverage tallies on fresh shards, external-truth deltas.
- **Mid-run hotfix policy**: hotfixes mix code generations within one corpus.
  If you hotfix, commit first, record the cutover timestamp, and ensure
  batches are separable (by stamp or by time) so the corpus can be split
  later. Prefer letting a non-critical issue ride to a planned relaunch.
- Spot-check fresh rows after every code change reaches production: confirm
  the fix appears in the data, not just in the tests.

## Release

- [ ] Final quality summary on the at-scale corpus (same dual-track QA as
      stage 3, sampled): score distribution, coverage histogram vs spec,
      telemetry totals.
- [ ] State the sampling frame, seed, inclusion probabilities/strata, reviewed
      counts and uncertainty. Oversampled failures must not be reported as an
      unweighted population pass rate. Report deduplication, contamination and
      held-out/downstream-value checks from the approved evaluation plan.
- [ ] Stratified raw-row read on the AT-SCALE data (scale changes behavior:
      judge drift, rare-path frequencies, external API behavior under load).
- [ ] Publish with batch metadata: row counts, commit(s), generation window,
      known caveats (e.g. "rows before <timestamp> predate fix X").
- [ ] If the corpus mixes generations, say so in the release notes, with the
      split key.

## Exit criteria

- Telemetry confirmed every designed capability fired at scale; final
  dual-track QA and an at-scale raw-row read passed.
- Data published (only on explicit human request) with batch metadata, and
  any mixed-generation split key stated.
- Postmortem written (below): gates added, review instructions and playbook
  updated, lessons recorded.

## Postmortem (closes the loop)

- What broke that no gate caught? Add the gate (ratchet).
- What did the human catch that agents missed? Update review instructions.
- What process step misfired? Update this playbook IN THE SAME CHANGE.
- One paragraph in `project_memory.md`: what the next generator should
  inherit from this one.

## Common failure modes

- Capabilities dark at scale because telemetry was "coming later".
- Untraceable corpora from uncommitted working-tree launches.
- Treating infrastructure flakiness (scheduler churn, node faults) as code
  bugs - keep an incident log; patterns across runs are infra, not you.
- Skipping the at-scale raw-row read because stage 3 passed: scale shifts
  distributions.
