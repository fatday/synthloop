# Design Spec: <generator name>

> Instantiated from synthloop templates/design_spec.md.
> Sections marked REQUIRED cannot be empty at the design gate.
> "None" is a permitted answer only with a written justification.

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

| Category / capability | Target share or usage floor | Demand mechanism |
| --- | --- | --- |
|  |  |  |

- Turn-type / difficulty mix:
- What QA measures this against (script/command):
- Cohort definitions (state any overlap and metric denominators):
- Directed functional smoke cases for rare capabilities:
- Minimum total / per-cohort validation sample sizes:
- Joint pass-rate target and per-cohort accepted-count floors:
- Frozen accepted-distribution shares / maximum TV-distance:
- Cycle / cost / wall-time limits and bounded retry policy:

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
- Pinned evaluation rubric version:
- Candidate rubric version (shadow only, if any):
- Independent review/refutation execution and evidence locations:

## 9. Open questions for the human

1.

## 10. FROZEN-BASELINE

> At approval, pin sections 1-5 and the evaluation rubric version.
> Never rewrite approved text during the autonomous loop.

- Approved design version / approval source / date:
- Last human-approved generator commit (rollback anchor):
- Input versions / existing infra metadata location:
- Per-project infra worktree / output prefix / shared-budget ownership:

## 11. AUTONOMOUS-DELTA (append-only)

| Date | Observed defect | Change within approved scope | Evidence / commit | Rationale | Ratified at checkpoint |
| --- | --- | --- | --- | --- | --- |

## 12. HUMAN-DECISIONS (append-only)

| Date | Decision | Approved version / scope | Source | Supersedes |
| --- | --- | --- | --- | --- |

## 13. Data-value evaluation

- Exact/near-duplicate checks and source lineage:
- Benchmark/eval contamination checks (keep test answers out of generation):
- Reviewer calibration set with human labels and disagreement handling:
- Independent holdout and target-model training/ablation check, or why deferred:
- At-scale sampling design and uncertainty reporting:
