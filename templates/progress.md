# Progress: <generator name>

> Human summary of state.json, the machine-readable resume point. Keep the
> header current; append ledger entries; never rewrite history. Run the shared
> resume check before starting an external job.

## Current state

- **Stage**: 0-context | 1-design | 2-implement | 3-quality-loop | 4-scale
- **Next action** (one line, concrete):
- **Blocked on** (if anything):
- **Open questions for the human**:
- **State revision / sub-stage cursor**:
- **Active batch / scheduler handle / output location**:
- **Review chunks completed / remaining**:
- **Clean-pass streak / validated fingerprint**:
- **Stop reason / cycle, cost and time consumed**:
- **Rollback anchor / current HEAD / autonomous commits**:

## Runbook

> Exact commands, filled during stage 2.

- Generate (smoke):
- Count rows / deltas:
- Coverage tally:
- Tests:
- Launch (scale):
- Validate state / resume / batch / scale gate:
- Reconcile a submitted job by batch/idempotency key:
- Cancel platform schedule (handle and command/tool):
- Live cost/time limits and in-flight/failed-attempt accounting:

## Gates

- Design approved by human: <date / source / baseline SHA-256>
- Scale approved by human: <date / source / exact launch-plan SHA-256>
- Publication authorized: <date / source / release scope>
- Unratified design deltas:

## Batch ledger

> One row per generation batch, append-only.

| Batch id | Date | Purpose | Manifest / review | Generated / B-reviewed | Joint rate | Coverage / drift | Verdict / action |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Session ledger

> Append one short entry per working session: what happened, what changed.

- <date>:
