# Design Spec: <generator name>

> Instantiated from synthloop templates/design_spec.md.
> Sections marked REQUIRED cannot be empty at the design gate.
> "None" is a permitted answer only with a written justification.
>
> **Frozen baseline (autonomous-loop contract).** §1, §2, §4 (categories +
> usage floors), and the Target-pass-rate floor are FROZEN at the design gate
> and re-frozen at each human checkpoint. The autonomous quality loop
> (`/cycle`) may append dated entries to §10 (Autonomous deltas) and §11 (Human
> decisions) but MUST NOT edit the frozen sections. "Major vs minor" and
> coverage drift are always judged against this frozen baseline; when a change
> is ambiguous, it is MAJOR. See `playbook/03_quality_loop.md` §3.5.

## 0. Context

- Target model / training stage / serialization format:
- Verbatim example of one training row in the target format:
- Adjacent datasets reviewed (and what this generator adds):
- Components reused from existing generators:
- External dependencies (APIs, sandboxes, corpora) with costs/quotas:
- Open unknowns:

## 1. Goals and non-goals

- The skill(s) this data teaches:
- Explicit non-goals:

## 2. Sample schema

- Fields and types:
- One fully-worked example row:

## 3. Generation architecture

- Stages / state machine:
- LLM calls (which model, where, for what):
- Deterministic vs sampled components; seeding scheme:

## 4. Behavior coverage spec (REQUIRED - numbers, not adjectives)

> FROZEN baseline. The usage-floor column is the per-cell coverage floor the
> autonomous loop must keep every cell at or above; a cycle whose accept-rate
> rises while any cell falls toward/below its floor is a rejection-wall STOP,
> not a pass. Floors may be RAISED autonomously; lowering one (or down-weighting
> a category below its floor) = removing a capability = HUMAN GATE.

| Category / capability | Target share or usage floor | Demand mechanism |
| --- | --- | --- |
|  |  |  |

- **Target-pass-rate floor** (REQUIRED): _____ (default 0.95). A batch passes only
  when **BOTH the Track-B reviewer (LLM) pass-rate AND the Track-A deterministic-
  check pass-rate on ACCEPTED rows ≥ this floor**, each measured INDEPENDENTLY
  (not merged into one combined number; both clear it on their own, worst-cohort).
  This is QUALITY (≥X% of rows that cleared the gates are good training data), NOT
  accept-rate/yield (the gates legitimately reject imperfect attempts, so yield
  runs below it). The loop may run `/cycle` at or above this; never below;
  lowering it is a human gate.
- **Coverage drift budget** (default: TV-distance 0.20 vs the frozen histogram,
  or 3 net-new autonomous subtypes) — crossing it forces a hard gate.
- Turn-type / difficulty mix:
- What QA measures this against (script/command):

## 5. Quality rules

- Hard rejects (deterministic):
- Scored dimensions (judged), with anchors:
- Known rejection-wall risks:

## 6. External Reality Checks (REQUIRED - all four)

1. External systems touched + INDEPENDENT source of truth for each:
2. Behavior-coverage telemetry (name the counters):
3. Provenance scheme (commit-before-launch, batch ids, row stamps):
4. Scale-only observables (rate limits, judge drift, accept-rate creep) and
   how each is watched:

## 7. Offline replayability plan

| External dependency | Offline twin / fixture | Same-code-path? |
| --- | --- | --- |
|  |  |  |

## 8. Review instruction v1

- Link: `review_instructions/v1.md`
- Generator-specific reviewer guidance (what to check, what to ignore):

## 9. Open questions for the human

1.

## 10. Autonomous deltas (append-only; written by `/cycle`, ratified by the human)

> Every minor-design tuning the loop applies on its own is logged here as a
> dated entry — NEVER edited into the frozen sections above. Each records: the
> cycle/commit, the change, its minor-classification rationale, and the
> usage counter + non-zero coverage floor it ships with. At a checkpoint the
> human ratifies entries into a new frozen baseline or reverts them; an
> unratified delta blocks scale.

| Date | Cycle / commit | Change | Minor-classification rationale | Counter + floor |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 11. Human decisions & non-goals ledger (append-only; human-owned)

> The checkable record of what the human approved, so the loop can tell when a
> change would contradict a past decision (→ MAJOR). Non-goals are never
> autonomously relaxed. Updated at the design gate and every checkpoint.

| Date | Decision / non-goal | Notes |
| --- | --- | --- |
|  |  |  |
