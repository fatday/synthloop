# Durable workflow state and checks

This is the shared runtime contract for Claude Code, Codex, and other agents.
`state.json` is the machine-readable resume point; `progress.md` is its human
summary. The small Python 3.10+ helper checks evidence and updates state. It
does not launch generators, schedule agents, infer human approval, or publish.

## Bootstrap and migration

Copy `templates/state.json` into the project and set `project_id`. During
design, fill `templates/baseline.json` as `baseline.json`. All supplied numbers
are proposed defaults, not approvals; fill the cost/time budgets and cohort
spec with the human. Cohorts in the helper are an exhaustive, mutually exclusive
partition of generated rows. Multi-label capability checks remain additional
project ratchets; do not silently discard them to fit this representation.

Export approved design sections 1-5 to approved_contract.md, leaving the changing
delta ledger outside that frozen file. The design gate freezes baseline.json,
the task contract and the evaluation rubric; baseline.json contains both the
contract and rubric SHA-256. Record the baseline's path and SHA-256 in state,
plus the real approval source and date:

```json
{
  "baseline": {"path": "baseline.json", "sha256": "<file sha256>"},
  "design_approval": {
    "source": "<user message or durable decision reference>",
    "approved_at": "<ISO-8601 timestamp>",
    "subject_sha256": "<baseline file sha256>"
  }
}
```

Do not manufacture approval from an agent summary. Existing authorization
remains valid across sessions when its subject still matches. An existing
project can migrate from progress.md: reconcile actual jobs, copy known state,
and preserve its ledgers. Missing artifacts/approvals are unknown, never assumed
passing. Legacy batches without evidence do not become clean passes by migration.
A changed approved baseline starts a new checkpoint directory with fresh state;
retain the previous directory and reference its history in progress.md.

## Commands

Run from the synthloop root; project-specific paths stay private:

```bash
python3 tools/synthloop.py validate-state data_projects/my-generator
python3 tools/synthloop.py resume data_projects/my-generator
python3 tools/synthloop.py update-state data_projects/my-generator --expected-revision 0 --patch /path/to/patch.json
python3 tools/synthloop.py check-batch data_projects/my-generator --manifest /path/to/run_manifest.json --review /path/to/review_result.json
python3 tools/synthloop.py record-review data_projects/my-generator --expected-revision 1 --manifest /path/to/run_manifest.json --review /path/to/review_result.json
python3 tools/synthloop.py check-gates data_projects/my-generator --plan /path/to/launch_plan.json --infra /path/to/generator-worktree
```

Paths in artifact descriptors are relative to the project directory, or absolute;
CLI file arguments are relative to the shell's working directory. Use SHA-256 of
the file bytes, not of a reserialized JSON object. The commands return JSON:
exit 0 = valid/result available, 1 = failed batch or resume stop, 2 = invalid
evidence/state or blocked scale gate. `check-gates` never runs the plan command.

`update-state` accepts a partial object for stage, cursor, next_action,
stop_reason, active_job, review_cursor, rollback_anchor, baseline and approvals.
It cannot overwrite history or revision. Every write takes `.state.lock`, checks
the expected revision, and atomically replaces state.json. On stale revision,
reload and reconcile; do not blindly retry. After a crash a lock can remain:
verify no writer is alive before removing it. Never auto-steal a lock.

## Resume and idempotency

Before starting work, run `resume`. Preserve its existing stop reason. An active
job always means **reconcile**, never launch again. Use `active_job` with `id`,
`batch_id`, and `backend`; reserve a stable batch/idempotency key in state BEFORE
submission, then store the scheduler handle. If submission acknowledgement was
lost, look up that key in the scheduler/output directory. If the outcome cannot
be established, stop for reconciliation rather than guessing that it failed.

Before semantic review, store `review_cursor` with `batch_id`, `planned_chunks`,
and `completed_chunks` (arrays of stable IDs). Persist each completed chunk's
evidence before marking it complete. Resume only remaining chunks. A completed
cursor with no remaining chunks means aggregate and record, not review again.
Clear active_job only after confirming the final output and its inventory.

`record-review` verifies evidence, rejects duplicate batch IDs, appends references
to history, and updates the cursor. The first clean pass requests a new-seed
confirmation run; the second consecutive clean pass on the same fingerprint
requests human review. Any failed/edited cycle breaks the streak. Changed code,
inputs, framework version, model, or baseline starts a new streak. Reusing an
identical raw batch under another ID/seed is not confirmation. Retrying
record-review after a lost acknowledgement cannot count the batch twice.

Set stop_reason for a hard gate, confirmed regression, recurrent defect, exhausted
budget, or uncertain external state. Clearing it requires recording the resolution
in progress.md and checking whether the action was already authorized. Do not ask
again solely because a new session started.

## Evidence files

Use the JSON templates; null fields must be populated before validation.
Archive a finalized manifest, review and input snapshots per batch, then never
overwrite them. Run inputs include resolved config, prompt bundle, evaluation
rubric, launch wrapper and dependency lock/environment export. Extra input roles
are allowed and participate in the fingerprint. The frozen task contract is
also a required input. The config input is the resolved behavior configuration;
per-run seed/output identity lives in the manifest, so a confirmation seed does
not change that config hash. `data` hashes the retained raw batch, including
rejects; `inventory` hashes a JSON array like:

```json
[{"id": "row-001", "cohort": "tool-use"}, {"id": "row-002", "cohort": "refusal"}]
```

Build inventory at generation time, before acceptance filtering. Record failed
generation attempts/retries separately in the batch report and cost ledger so
they cannot disappear from throughput/cost accounting. `generated_count` means
all emitted rows, not all attempts. If no rows are emitted, record an infra
failure and incurred spend in the incident log, not a fake passing batch.

The review has one entry per inventory ID:

```json
{"id": "row-001", "a_pass": true, "b_pass": null}
```

`b_pass: null` means unreviewed. Track A covers every emitted row, including
rejects. Track B covers all rows for a validation pass; full joint rate and
worst-cohort rates are calculated from the row-level intersection. A sampled
review returns observed metrics and a conservative observed lower bound, but
cannot establish a full-batch pass. At-scale sampling needs the approved sampling
plan and uncertainty report; the helper does not implement a statistical estimator.

Review flags attest to completed raw reading, refutation and ratchet checks;
link their actual evidence in the accompanying Markdown summary. `cost_usd` and
`wall_seconds` cover the cycle including generation, review, retries and repair.
Record functional smokes and scale costs outside validation history. The helper
checks accumulated validation-cycle budgets before recommending another cycle.
The project launcher must also enforce live job limits and account for unrecorded
in-flight/failed work; these offline checks are not a spending daemon.

## Scale authorization

After two clean passes, finish the launch plan before requesting approval. Copy
the batch check's fingerprint, list exact command/row/cost/time limits, resolve
all unratified deltas, and hash the actual scale config. `current_inputs` points
to live counterparts of every archived validation input. The scale config may
change volume/concurrency only; behavior changes need new validation. Record the
scale approval against the hash of the entire plan, with date and source.

Immediately before launch, run check-gates. It rechecks both pass artifacts,
input hashes, exact approved plan, and clean generator/framework HEADs. Use the
separate approved scale budget, not the exhausted smoke budget. Keep the worktree and
inputs unchanged between checking and launching. A scale approval is not a
publication approval; publication still requires explicit authorization.

## Parallel projects and limits

Each project uses its own generator worktree, output prefix and job key. Only one
writer owns a project at a time. Shared ENVIRONMENT.md/playbook changes use a
single writer or ordinary branch/merge review; separate project folders do not
isolate a shared infra HEAD. Check and reserve shared API/compute budgets too.

Checks detect accidental drift, malformed evidence and stale state. They are not
a security boundary against an agent rewriting the checker, fabricating review
flags or approvals, or bypassing the launcher. Human-owned baselines/ratchets and
independent evidence remain part of the contract. JSON syntax alone does not
prove a review is correct. Tests are offline protocol tests, not live model evals.
