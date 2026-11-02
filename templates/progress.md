# Progress: <generator name>

> The resume point for any agent or human. Keep the header current; append
> ledger entries; never rewrite history.
>
> Keep it short (CLAUDE.md "State budgets"): current state, the pinned sections,
> the last ~10 entries of each ledger and the last ~5 cursor entries, each at
> most ~1,000 characters. At each stage exit, or past ~25 KB, move older entries
> and finished-investigation notes verbatim to `progress_ledger.md`
> (append-only, newest first). List live worktrees under Runbook with their
> branch and purpose.

## Current state

- **Stage**: 0-context | 1-design | 2-implement | 3-quality-loop | 4-scale
- **Next action** (one line, concrete):
- **Cycle cursor** (autonomous loop): `<n> · SMOKE|REVIEW|FIX&ADD|IDLE · <resume handle>`
- **Blocked on** (if anything):
- **Open questions for the human**:

## Smoke spec

> Pinned ONCE — elicited by `/smoke` on the first run if absent, then launched
> verbatim. `/smoke` and `/cycle` never re-ask unless the human says to change
> it, and each launch is asserted to match this spec (mismatch → STOP).

- Generators (which / bring-up order):
- Batch size (bs):
- Model:
- Time-box per run:
- Nodes per generator:
- max-model-len / other launch flags:

## Runbook

> Exact commands, filled during stage 2.

- Generate (smoke):
- Count rows / deltas:
- Coverage tally:
- Tests:
- Launch (scale):

## Gates

- Design approved by human: <date / link>
- Scale approved by human: <date / link>

## Batch ledger

> One row per generation batch, append-only.

| Batch id | Date | Commit | Size | QA verdict | Notes |
| --- | --- | --- | --- | --- | --- |

## Session ledger

> Append one short entry per working session: what happened, what changed.

- <date>:
