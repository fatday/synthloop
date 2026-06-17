---
name: cycle
description: Run ONE full inner-loop iteration for a generator project - smoke generation, dual-track review, and safe (non-code) repair - then decide whether to loop again or stop at a hard gate. Designed to be driven hands-off via `/loop /cycle <name>`. Usage - /cycle <generator-name> [target-pass-rate]
---

# /cycle <generator-name> [target-pass-rate]

One pass of the quality loop, end to end, so the human types one command (or
none, under `/loop`) instead of `/smoke` then `/review` then `/repair`. This is
a thin router over the existing stage skills + `playbook/03_quality_loop.md`; it
does NOT introduce new quality rules, only sequences them and adds the
stop/continue decision.

`target-pass-rate` defaults to **0.95** (95%). It is the Track-A accept-rate
floor used in the pass test below. Read it as a fraction or a percent.

## Preconditions (STOP if unmet)

- Project exists and is at stage 2-implement complete or later (`/smoke`'s
  precondition). If not, stop and say what's missing.
- Read `data_projects/ENVIRONMENT.md`, the project's `progress.md`,
  `project_memory.md`, and the latest `review_instructions/v*.md` before acting.

## The iteration

1. **Smoke** — run `/smoke <name>` (commit-for-provenance, generate, Track A
   coverage tally, quick Track C read). Record the batch in the ledger.
2. **Review** — run `/review <name>` (Track A deterministic, Track B agent
   review WITH the refutation pass + kill-rate, Track C stratified raw read,
   one verdict written per `review_rubric.md`). Capture: the accept-rate, the
   list of *surviving* (post-refutation) findings, and each finding's repair
   scope (prompt/threshold/keyword vs CODE).
3. **Decide** (in this order — first match wins):

   a. **CODE fix required** — any surviving finding whose fix touches code
      (parsers, scoring, schema rendering, state machines). STOP. The playbook
      forbids auto-editing code; present the diagnosis-needed findings and hand
      to `/repair` for a human-supervised fix. Do not loop.

   b. **PASS** — Track-A accept-rate ≥ target AND no surviving critical
      findings AND coverage within spec AND the Track-C read raised nothing
      new. Record "pass" in the ledger. If this is the **second consecutive**
      passing cycle, STOP and present the stage-3 human gate (one pass can be
      luck — see 03_quality_loop exit criteria). If it's the first pass, the
      loop MAY continue to confirm; say so.

   c. **SAFE repair** — the only surviving findings are prompt / steering /
      threshold / keyword-list / sampling-weight changes. Run `/repair <name>`
      restricted to that scope: write the diagnosis, patch, add the ratchet
      guard, do the gate-impact check, version review instructions if reviewer
      behavior changed, record in `project_memory.md`. Then this iteration ends
      with next-action = re-run `/cycle` — i.e. loop again.

## Stop conditions (any one ends the loop)

- Two consecutive passing cycles → **stage-3 human gate** (hard gate; never
  auto-proceed to `/scale`).
- A finding needs a **code fix** → hand to `/repair` (human-supervised).
- **Oscillation**: the same metric flips direction twice across cycles, or the
  same finding-class reappears after a repair claimed to fix it → STOP and
  diagnose; do not keep patching.
- **Safety cap**: stop after 6 cycles without a pass and summarize, rather than
  burn compute indefinitely. (Override by re-invoking.)
- Any precondition or infra failure (generation crash, missing data) → STOP
  with the error.

## Write back (every iteration, even on STOP)

- Append a cycle row to the ledger in `progress.md`: cycle #, batch id, commit,
  accept-rate, verdict, action taken (repair scope / pass / stop-reason).
- Update the `progress.md` Current-state header and the single next action.
- Record any diagnosis/lesson in `project_memory.md`; promote generalizable
  lessons to `playbook/` in the same change.

## Driving it hands-off

- Repeat until target: `/loop /cycle <name>` (self-paced; re-invokes after each
  cycle finishes). The loop naturally halts when this skill hits a STOP
  condition above and stops setting a "loop again" next action.
- One cycle at a time: just type `/cycle <name>` whenever you want the next pass.
- Custom target: `/cycle <name> 0.9` (or `/loop /cycle <name> 0.9`).

This skill NEVER crosses a human gate, NEVER edits generator code on its own,
and NEVER runs `/scale`. Those remain explicit human actions.
