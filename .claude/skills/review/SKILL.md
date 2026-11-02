---
name: review
description: Run the dual-track QA review on the latest batch of a generator project - deterministic checks, chunked agent review with refutation pass, raw-row read, and a verdict. Usage - /review <generator-name>
---

# /review <generator-name>

1. Read `data_projects/<name>/progress.md`, the design spec's coverage numbers,
   and the LATEST `review_instructions/v*.md`. Read
   `playbook/03_quality_loop.md` section 3.2 and `playbook/review_rubric.md`.
2. **Track A - deterministic**: run the post-data sweep over the landed batch
   (`scripts/track_a_checks.py`) — structural invariants HARD FAIL; capture the
   quality-signal table for the summary. Coverage histogram vs the spec's
   numbers, capability counters vs floors, ratchet checks, accept-rate vs
   previous batch.
3. **Track B - agent review**: chunk the batch 25-50 rows per reviewer with
   the current review instruction. Reviewers cite row ids + verbatim
   evidence and receive FULL rows (never truncate). **Each finding is
   ROW-LEVEL**: it carries the row's stable id (seed) + line index, the
   generator + mode/backend cohort, a problem label (controlled vocabulary, see
   `templates/review_summary.md`), severity (T1/T2), and a one-line detail with
   the offending value — this is what populates the per-row table. Then run the
   refutation pass: an independent reviewer per finding, given the full row,
   tries to disprove it. Drop refuted findings; keep a count of how many died (a
   high refutation rate means the review instruction needs tightening).
   **Then the control chunk**: one more reviewer, same prompt and model,
   on a FROZEN anchor set (~50 rows from a pinned earlier batch, re-staged
   deterministically). Report the headline beside the control's number and
   its pinned original; a move the control also makes is instrument drift.
   Identical rows can score tens of points apart across reviewer instances even
   under a pinned rubric — without a control, a series trend is unanchored.
4. **Track C - stratified raw read**: a few rows per category and turn type,
   oversampling sub-perfect scores, refusals, and empty results. Ask "is
   this what we want a model to learn".
5. **Write the review summary** to `reviews/v<N>.md` from
   `templates/review_summary.md` (create `reviews/` if absent). **`N` is the
   next number after the HIGHEST `v*.md` already in `reviews/` — `ls` the
   directory and check before writing, never infer N from the last review you
   happen to remember.** Review files are append-only history; reusing a number
   silently destroys an earlier review, and a long-running project restarted
   after a break is exactly where the counter gets lost. If you find a review
   was clobbered, restore it from git and renumber yours to the free slot.
   Fill EVERY
   section — verdict, the **per-row problem table** (one line per confirmed
   row-level finding: row seed/#, generator, mode/backend, severity, problem
   label, detail), the problem tally, the Track-A digest, coverage/yield deltas
   vs the prior version, systemic findings, what was clean, next action.
   Evidence verbatim, never truncated. This file is the human's scannable view
   of how the batch went — quality of writing matters.
6. Record the verdict + a link to `reviews/v<N>.md` in the batch ledger. If
   pass: present to the human for the gate. If fail: hand the confirmed findings
   to `/repair`.
