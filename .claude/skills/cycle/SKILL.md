---
name: cycle
description: Run ONE iteration of the autonomous quality loop for a generator — smoke, dual-track review, then autonomously repair EVERY fix class (prompt/code/constants/minor-design tuning) under monotonic, tamper-evident guards — then loop, or stop at the target checkpoint or a hard gate. Drives hands-off via `/loop /cycle <name>`. Usage - /cycle <generator-name> [target-pass-rate]
---

# /cycle <generator-name> [target-pass-rate]

One iteration of the quality loop, end to end, so the human types one command
(or none, under `/loop`) instead of `/smoke` then `/review` then `/repair`. It
sequences those stage skills and adds the stop/continue decision. Unlike the
older version, this loop **autonomously applies every fix class** (prompt,
code, constants, minor design tuning) — but only inside the guard rails below,
which exist so autonomy cannot quietly trade data quality for a passing metric.

`target-pass-rate` defaults to **0.95** but may never run below the
human-set **target floor** recorded in the design spec (raising the bar is
fine; lowering it below the floor is a HARD GATE). It is read as a fraction or
a percent.

## The one idea behind every rule here

The loop optimizes a metric it can also *cheat*. It can hit "95% accept-rate"
by genuinely fixing the generator, or by rejecting the hardest honest rows,
down-weighting a hard capability, relaxing the rubric it is graded by, or
weakening its own ratchet tests — and every per-cycle check stays green while
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

## The iteration

1. **Smoke** — run `/smoke <name>` (commit-for-provenance, generate, Track A
   coverage tally, quick Track C read). Record batch id + commit in the ledger.
   The reviewed batch's stamped commit MUST equal current HEAD; rows from an
   older commit are invalid for this cycle's accept-rate.
2. **Review** — run `/review <name>` (Track A deterministic; Track B agent
   review WITH refutation pass + kill-rate; Track C stratified raw read; one
   verdict per `review_rubric.md`). Score the pass test with the **rubric
   version pinned to the last human checkpoint** — do not score against a
   rubric this loop edited. Capture: accept-rate over the FULL batch,
   per-coverage-cell accepted volume vs the baseline floor, the cumulative
   drift vs baseline, the surviving (post-refutation) findings, and each
   finding's fix scope.
3. **Propose (don't adopt)** — note coverage gaps and quality/creative
   improvement ideas to `progress.md` as **proposals**. Ideas that merely close
   a logged, observed finding on the approved surface feed step 4. Ideas that
   **expand scope** (new capability/subtype, new creative direction) are taste
   calls: they are logged and surfaced at the checkpoint, NOT applied
   autonomously (Invariant 5).
4. **Decide** (first match wins):

   a. **HARD GATE** — STOP and present, never cross alone, if the needed change
      is: a **major design pivot** (touches the frozen baseline — purpose,
      scope, schema/format/data contract, target floor, a declared non-goal, or
      removing/▾-floor-ing a declared capability); **any net-tightening of
      acceptance** (a new/tightened gate, or a code change that would reject,
      drop, filter, or fail rows, or a down-weight that pushes any baseline cell
      below floor); a change that would **relax the judge** (Tier-1 definition,
      what reviewers flag) or **weaken a ratchet test/fixture**; **scope
      expansion / creative direction**; or **cumulative drift** over budget. When
      minor-vs-major is not unambiguous — anything touching schema/format, a
      non-goal, or readable as expanding scope — **default to HARD GATE**.

   b. **PASS** — only on a **clean cycle** (this cycle applied NO code/constant/
      design edit, so the reviewed rows came from current HEAD) where: accept-rate
      ≥ target AND **every baseline coverage cell ≥ its floor** AND cumulative
      drift within budget AND no surviving critical findings AND Track-C raised
      nothing new. Record "pass (provisional)" and **STOP — hand back to the
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
   *loosen* acceptance; **any net-tightening is human-gated**. PASS needs
   accept-rate ≥ target AND every baseline cell ≥ floor AND drift in budget —
   accept-rate alone never passes, and "accept-rate up + any cell down" is a
   rejection-wall STOP.
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
5. **Repair, not expand.** Autonomy restores quality on the approved surface.
   Scope expansion and creative direction are proposed every cycle and applied
   only with explicit human direction (at the checkpoint or a hard-gate stop).

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
- Update the Current-state header and the single next action.
- **Every STOP includes** a cumulative coverage + accept-rate delta table since
  the last human checkpoint (per cell, with the verbatim sample of rows
  accepted then but rejected now), the current HEAD, the rollback anchor, and
  the list of autonomous commits made this loop.
- Record diagnoses/lessons in `project_memory.md`; promote generalizable
  lessons to `playbook/` in the same change. Record the minor/major
  classification + one-line rationale for every applied design delta.

## Driving it hands-off

- Repeat until the checkpoint: `/loop /cycle <name>` (self-paced; re-invokes
  after each cycle). It halts at any stop condition and stops setting a "loop
  again" next action.
- One cycle: `/cycle <name>`. Custom target (≥ floor): `/cycle <name> 0.97`.

## Bright lines (the loop NEVER does these on its own)

- `/scale` or any release.
- Cross a major-design-pivot gate, net-tighten acceptance, relax the judge, or
  weaken a ratchet — all are propose-and-stop, never apply.
- Adopt a scope expansion / creative direction without human direction.
- Run below the target floor, edit a frozen baseline section, or delete/
  regenerate existing data on its own initiative.
