---
name: cycle
description: Self-driving autonomous quality loop for a generator — repeats smoke → dual-track review → fix&add (autonomously repairing EVERY fix class - prompt/code/constants/minor-design tuning, under monotonic tamper-evident guards) on its own across iterations until the target checkpoint or a stop/hard-gate. `/cycle <name>` IS the loop (no separate `/loop` needed). Usage - /cycle <generator-name> [target-pass-rate]
---

# /cycle <generator-name> [target-pass-rate]

The autonomous quality loop: it **self-drives** smoke → review → fix&add and
**repeats across iterations on its own** until the target checkpoint or a stop
condition — so the human types one command instead of `/smoke` then `/review`
then `/repair`, over and over. `/cycle <name>` IS the loop; no separate `/loop`
is needed (`/loop /cycle` only adds a redundant heartbeat). It sequences those
stage skills and **autonomously applies every fix class** (prompt, code,
constants, minor design tuning) — but only inside the guard rails below, which
exist so autonomy cannot quietly trade data quality for a passing metric.

`target-pass-rate` defaults to **0.95** but may never run below the
human-set **target floor** recorded in the design spec (raising the bar is
fine; lowering it below the floor is a HARD GATE). It is read as a fraction or
a percent.

## The one idea behind every rule here

The loop optimizes a metric it can also *cheat*. The pass bar is **BOTH the
Track-B reviewer (LLM) pass-rate AND the Track-A deterministic-check pass-rate on
accepted rows ≥ target, independently** (quality, not accept-rate/yield) — and it
can hit the quality bar by genuinely fixing the generator, or by cheating:
cherry-picking (tighten gates → accept only easy rows so the survivors look
clean), relaxing the rubric it is graded by, down-weighting a hard capability,
or weakening its own ratchet tests — and every per-cycle check stays green while
the human sees only the survivors. So autonomy is allowed **only when it cannot
narrow the data behind your back**. Five invariants enforce that; they are
stated canonically in `playbook/03_quality_loop.md` §3.3–§3.5 and
`principles.md` #2/#3/#9, and summarized in "Invariants" below.

## Preconditions (STOP if unmet)

- Project at stage 2-implement complete or later (`/smoke`'s precondition). If
  not, stop and say what's missing.
- Read `data_projects/ENVIRONMENT.md`, the project's `progress.md`,
  `project_memory.md`, and the latest `review_instructions/v*.md`.
- **At loop entry** record in `progress.md`: (a) the **rollback anchor** = the
  last human-approved commit hash of the generator code; (b) the **frozen
  baseline** reference = the design-spec sections + coverage histogram/floors +
  non-goals + target floor as of the last human checkpoint. The loop may append
  dated deltas but never edits these frozen sections.

## Resume (stage cursor)

The loop can be interrupted anywhere — mid-smoke (a multi-hour job), mid-review,
or mid fix-&-add. To resume on its own without redoing work, every cycle keeps a
**stage cursor** in `progress.md`'s Current-state header and reads it on entry:

`Cycle cursor: <n> · <SMOKE|REVIEW|FIX&ADD|IDLE> · <resume handle>`

- **On entry, read the cursor first.** If a cycle is in flight, RESUME from its
  sub-stage rather than restarting:
  - `SMOKE` (handle: job id + output dir) → if the job is still running,
    re-arm the monitor and wait; if rows landed, advance to REVIEW; if it
    failed, diagnose.
  - `REVIEW` (handle: batch path + which of Track A/B/C are done) → finish the
    unfinished track, then decide.
  - `FIX&ADD` (handle: the findings/adds and which are already applied) →
    continue with the next un-applied item; never re-apply a done one.
- **Update the cursor at every sub-stage transition** (and on STOP), so a fresh
  session or a re-fired `/loop` picks up exactly where it left off. Clear it to
  `IDLE` when a cycle completes (pass/stop). The cursor is the single source of
  truth for "where am I" — keep it COMPLETE at all times so harness
  auto-compaction (or a human `/compact`) is LOSSLESS (CLAUDE.md #7); after any
  compaction, re-read the cursor and continue. On a clearly long run, write a
  fresh full checkpoint and tell the human it's safe to `/compact`.

## The iteration

1. **Smoke** — run `/smoke <name>` (generate, Track A coverage tally, quick
   Track C read). `/smoke` pins the **Smoke spec** on the first run if none
   exists (the one time it asks), then on every run launches that pinned spec
   verbatim with an echo-and-assert drift check — never re-asking and never
   improvising the config unless the human changes the spec. Record batch id +
   provenance in the ledger. The reviewed batch's stamped commit/working-tree
   state MUST equal current HEAD; rows from older code are invalid for this
   cycle's accept-rate.
2. **Review** — run `/review <name>`. Track A first: the **post-data sweep**
   (`scripts/track_a_checks.py`) over the WHOLE landed batch — STOP the cycle on
   any structural HARD FAIL (zero-usage cell, unparseable call/result,
   unadvertised tool, missing required arg); read its quality signals as a cheap
   pre-Track-B read (they often confirm/refute the last fix before reviewers
   spend tokens). Then Track B agent review WITH refutation pass + kill-rate;
   Track C stratified raw read; one verdict per `review_rubric.md`. Score the pass test with the **rubric
   version pinned to the last human checkpoint** — do not score against a
   rubric this loop edited. Capture: accept-rate over the FULL batch,
   per-coverage-cell accepted volume vs the baseline floor, the cumulative
   drift vs baseline, the surviving (post-refutation) findings, and each
   finding's fix scope. **Write `reviews/v<N>.md`** from
   `templates/review_summary.md` every cycle — including the per-row problem
   table (row seed/#, generator, mode/backend, severity, label, detail) — so the
   human has a durable, scannable record of each iteration; link it in the ledger.
3. **Fix & add** — collect BOTH the surviving findings AND coverage/quality
   improvements (new task subtypes, richer scenarios) that strengthen the
   **approved surface**; both feed the repair pipeline in step 4 autonomously.
   Each ADD ships with a usage counter + a non-zero coverage floor and is
   tracked as its own cohort (so it can't dilute the pass metric). Only changes
   that go BEYOND the approved surface — a capability the spec doesn't imply, a
   new creative direction, a major pivot — are logged to `progress.md` and
   surfaced at the checkpoint, not applied (Invariant 5).
4. **Decide** (first match wins):

   a. **HARD GATE** — STOP and present, never cross alone, if the needed change
      is: a **major design pivot** (touches the frozen baseline — purpose,
      scope, schema/format/data contract, target floor, a declared non-goal, or
      removing/▾-floor-ing a declared capability); **any net-tightening of
      acceptance** (a new/tightened gate, or a code change that would reject,
      drop, filter, or fail rows, or a down-weight that pushes any baseline cell
      below floor); a change that would **relax the judge** (Tier-1 definition,
      what reviewers flag) or **weaken a ratchet test/fixture**; **expansion
      beyond the approved surface** (a capability/direction the spec doesn't
      imply); or **cumulative drift** over budget. When
      minor-vs-major is not unambiguous — anything touching schema/format, a
      non-goal, or readable as expanding scope — **default to HARD GATE**.

   b. **PASS** — only on a **clean cycle** (this cycle applied NO code/constant/
      design edit, so the reviewed rows came from current HEAD) where **BOTH
      quality tracks clear target INDEPENDENTLY** (a two-track AND — never a
      "combined"/blended number): the **Track-B reviewer (LLM) pass-rate on
      ACCEPTED rows ≥ target** AND the **Track-A deterministic-check pass-rate ≥
      target** (the deterministic track is a conservative FLOOR — high there does
      NOT excuse a failing LLM track, and vice versa), both scored on the rubric/
      checks pinned to the last checkpoint, **for every established cohort (the
      worst cohort, not the blended average)** AND **every baseline coverage cell
      ≥ its floor** (so quality isn't gamed by shedding hard rows) AND cumulative
      drift within budget AND no surviving critical findings AND Track-C raised
      nothing new. Record
      "pass (provisional)" and **STOP — hand back to the
      human** for review + new direction. A pass is provisional until you
      confirm it; the human checkpoint is the authoritative confirmation. Never
      auto-`/scale`.

   c. **AUTONOMOUS REPAIR** — the surviving findings can be fixed by *fixing the
      generator* or *loosening* acceptance (never net-tightening it). Run
      `/repair <name>`; it applies each fix at its natural scope with the full
      guard chain (diagnose→fix→fail-on-parent test→ratchet→gate-impact→
      adversarial verify of the fix with a rejection-wall mandate→commit). Any
      single fix that hits a 4a condition is split off and escalated, not
      applied. Then next-action = re-run `/cycle` (loop). Because this cycle
      edited code, it **cannot also pass** this cycle — the fix must be
      validated on a freshly-generated, same-commit batch next iteration.

## Invariants (the guard rails; canonical in the playbook)

1. **Frozen baseline.** Approved spec sections + coverage histogram/floors +
   non-goals + target floor are frozen at each human checkpoint. The loop only
   appends dated delta blocks; "major" is always judged against the frozen
   baseline, never the drifted state.
2. **Acceptance monotonicity.** Autonomous repair may fix the generator or
   *loosen* acceptance; **any net-tightening is human-gated**. PASS needs **BOTH
   the Track-B (LLM) quality pass-rate AND the Track-A deterministic-check
   pass-rate on accepted rows ≥ target** (each independently, worst-cohort — not
   merged into one number) AND every baseline cell ≥ floor AND drift in budget —
   the quality bars alone never pass (they can be cherry-picked by shedding hard
   rows), so they are yoked to the coverage floor + monotonicity; "quality up +
   any cell down" is a rejection-wall STOP. Yield (accept-rate) is tracked but is
   never the pass bar.
3. **Judge & ratchet are human-owned, append-only.** The loop may add/tighten
   reviewer checks and add ratchet tests; it may never relax a Tier-1/critical
   definition, weaken what reviewers flag, or weaken/skip/delete/narrow an
   existing ratchet test or fixture. Diff the test files each cycle; STOP if any
   existing assertion/fixture was removed or loosened.
4. **Provenance: clean-cycle-to-pass.** Any edit invalidates the prior batch
   (discard, never count it) and is committed; a new test must FAIL on the
   parent commit and PASS on the fix. A cycle that edited anything cannot pass.
   Code touching scoring/parsing/schema/checks is replayed against retained
   prior rows; if it would now reject/re-label accepted rows, that is a cutover
   — STOP and record it.
5. **Fix & add on the approved surface; don't redefine it.** Autonomy fixes
   findings AND adds coverage/quality on the approved surface — each addition
   ships with a counter + non-zero floor, tracked as its own cohort. Honest 95%
   is **per-cohort**: the WORST established cohort must meet target (not the
   blended average), and floors are raise-only — so adding easy material can't
   fake a pass. Redefining the surface (a capability the spec doesn't imply, a
   new creative direction, a major pivot) is applied only with human direction.

## Auto-stops (end the loop with no human needed to stop it)

- **Target hit** → STOP + hand back (4b).
- **Hard gate** (4a) → STOP + wait for human.
- **Rejection-wall signal** → accept-rate rose while any coverage cell shrank,
  or cumulative drift crossed budget → STOP + present the drift/coverage delta.
- **Oscillation** → same metric flips direction twice, or a finding-class
  recurs after a repair claimed to fix it → STOP + diagnose (stop patching).
- **Regression** → accept-rate drops with no matching coverage gain, any
  coverage cell drops vs prior cycle, or a ratchet test that passed now fails →
  STOP + diagnose. A STOP-to-diagnose may resume ONLY if the resolution is a
  generator/data fix; if the only fix is to weaken a gate/threshold/rubric/test,
  the loop stays stopped and presents to the human.
- **Safety cap** → stop after 6 cycles without a pass and summarize.
- **Infra failure** (generation crash, missing data) → STOP with the error.

## Write back (every iteration, even on STOP)

- Append a cycle row to the ledger in `progress.md`: cycle #, batch id, commit,
  accept-rate (over full batch), per-cell coverage vs floor, drift, verdict,
  action taken (fix scope / pass / stop-reason).
- Update the Current-state header, the single next action, and the **stage
  cursor** (sub-stage + resume handle) — refresh the cursor at every sub-stage
  transition, not only at cycle end, so an interrupted loop resumes precisely.
- **Every STOP includes** a cumulative coverage + accept-rate delta table since
  the last human checkpoint (per cell, with the verbatim sample of rows
  accepted then but rejected now), the current HEAD, the rollback anchor, and
  the list of autonomous commits made this loop.
- Record diagnoses/lessons in `project_memory.md`; promote generalizable
  lessons to `playbook/` in the same change. Record the minor/major
  classification + one-line rationale for every applied design delta.

## Self-continuation (how `/cycle` loops on its own)

`/cycle` does not stop after one pass. After it launches a smoke or applies a
fix, it **arms a monitor on the job (+ a fallback heartbeat) so the loop
re-enters at the next milestone** (smoke finished, rows landed, fix applied) and
continues — smoke → review → fix&add → repeat — without the human re-typing
anything. It halts and hands back ONLY at: the target checkpoint (4b), a hard
gate (4a), or an auto-stop. Update the stage cursor at every transition so a
re-entry resumes precisely.

Caveat: self-continuation rides an in-session monitor + heartbeat, which end
when the session closes. The generation jobs persist and `progress.md` (the
stage cursor) is the resume point, so a fresh session picks up exactly where it
left off — re-arm the monitor on the still-running/completed job and continue.

## Driving it hands-off

- `/cycle <name>` self-loops to the checkpoint (see Self-continuation above).
  Custom target (≥ floor): `/cycle <name> 0.97`. To pause, just say so.
- `/loop /cycle <name>` is equivalent + adds a scheduled heartbeat (useful if a
  monitor might miss a wake); not required.

## Bright lines (the loop NEVER does these on its own)

- `/scale` or any release.
- Cross a major-design-pivot gate, net-tighten acceptance, relax the judge, or
  weaken a ratchet — all are propose-and-stop, never apply.
- Adopt a scope expansion / creative direction without human direction.
- Run below the target floor, edit a frozen baseline section, or delete/
  regenerate existing data on its own initiative.
