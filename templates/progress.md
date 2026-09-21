# Progress: <generator name>

> The resume point for any agent or human. Keep the header current; append
> ledger entries; never rewrite history. Reconcile referenced jobs and outputs
> before starting another run.

## Current state

- **Stage**: 0-context | 1-design | 2-implement | 3-quality-loop | 4-scale
- **Next action** (one line, concrete):
- **Blocked on** (if anything):
- **Open questions for the human**:
- **Current sub-stage**:
- **Active batch / scheduler handle / output location**:
- **Review chunks completed / remaining**:
- **Consecutive clean passes / code and input versions**:
- **Stop reason / cycle, cost and time consumed**:
- **Rollback anchor / current HEAD / autonomous commits**:

## Runbook

> Exact commands, filled during stage 2.

- Generate (smoke):
- Count rows / deltas:
- Coverage tally:
- Tests:
- Launch (scale):
- Reconcile a submitted job by batch/idempotency key:
- Cancel platform schedule (handle and command/tool):
- Live cost/time limits and in-flight/failed-attempt accounting:

## Gates

- Design approved by human: <date / source / approved spec and rubric versions>
- Scale approved by human: <date / source / approved launch command, volume and budget>
- Publication authorized: <date / source / release scope>
- Unratified design deltas:

## Batch ledger

> One row per generation batch, append-only.

| Batch id | Date | Purpose | Commit / config / review | Generated / B-reviewed | Joint rate | Coverage / drift | Verdict / action |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Session ledger

> Append one short entry per working session: what happened, what changed.

- <date>:
