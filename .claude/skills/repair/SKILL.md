---
name: repair
description: Diagnose-then-patch the confirmed findings from the latest review of a generator project. Applies every fix class (prompt/code/constants/minor-design tuning) autonomously under monotonic, provenance-safe guards; escalates net-tightening, judge/ratchet weakening, and major pivots to the human. Usage - /repair <generator-name>
---

# /repair <generator-name>

1. Read the latest review summary, `data_projects/<name>/project_memory.md`
   (known traps), and `playbook/03_quality_loop.md` §3.4–§3.5. Note the frozen
   baseline (coverage floors, non-goals, target floor) and the rollback anchor.
2. For each confirmed finding, **write the diagnosis before touching anything**:
   the mechanism traced to root cause, reproduced offline (replay twins/
   fixtures). If you cannot reproduce or explain it, say so and investigate —
   do not patch blind.
3. **Classify the fix, then apply at its natural scope:**
   - **Generator fix or acceptance-LOOSENING** (prompt/steering wording,
     relaxing an over-strict threshold/keyword/gate, fixing a parser/scorer so
     honest rows pass): apply directly. Code changes get a minimal fix + a NEW
     test that **fails on the parent commit and passes on the fix** (record both
     results — a test that passes pre-fix is not a ratchet) + run the suite.
   - **Minor design tuning** (raising a coverage weight/floor, a subtype the
     frozen spec already implies): write it as a dated entry in the spec's
     append-only **AUTONOMOUS-DELTA** section (never edit frozen text), with a
     usage counter and a non-zero coverage floor, and the minor/major rationale.
   - **ESCALATE (propose + STOP, do not apply)** anything that net-tightens
     acceptance (new/tightened gate, code that rejects/drops/filters rows, a
     down-weight pushing any baseline cell below floor), relaxes the judge
     (Tier-1 definition, what reviewers flag), weakens/skips/deletes an existing
     ratchet test or fixture, expands scope / adds a creative direction, or
     touches the frozen baseline. Present diagnosis + before/after accept-rate +
     the verbatim newly-rejected sample. When minor-vs-major is unclear, escalate.
4. **Ratchet**: every confirmed finding gets a permanent guard (test,
   validation, counter alert). Ratchet tests are append-only — add, never weaken.
5. **Gate-impact check** (runs on the code path too, not just thresholds): any
   change that can reject/drop/filter/fail rows is a gate. Compare accept-rate
   and per-cell coverage before vs after on the same batch; read a verbatim
   sample of newly-rejected rows. A unit test passing is necessary but NOT
   sufficient — if the change net-reduces acceptance in any cell, it is
   human-gated (step 3 ESCALATE), not autonomous.
6. **Adversarial verification of the fix** (not just the finding): an
   independent pass must specifically try to show the fix raised accept-rate by
   excluding honest rows rather than by improving the generator — pull the rows
   newly-rejected vs the prior batch, read them verbatim, and affirmatively
   certify they are genuinely-bad (not honest-but-imperfect). Inability to
   certify → present to the human, do not keep the fix.
7. **Provenance**: commit the fix (stamp the hash). The change invalidates rows
   from the prior commit — discard/quarantine them; they do not count toward the
   next cycle's accept-rate. For changes to scoring/parsing/schema/checks,
   replay against retained prior rows; if they would now reject/re-label
   accepted rows, record a cutover (do not silently keep mixed-label data).
8. If reviewer behavior should change, write `review_instructions/v<n+1>.md`
   with a changelog line — **additive/tightening only**; any edit that could
   lower the pass bar is a major change → escalate.
9. Record each diagnosis + change + minor/major rationale in `project_memory.md`
   (one paragraph). If a lesson generalizes, ALSO update `playbook/` in the same
   change.
10. Update `progress.md` next action to re-run `/cycle` (the loop continues; a
    cycle that applied a fix cannot itself pass — the fix is validated on a
    fresh same-commit batch next iteration).
