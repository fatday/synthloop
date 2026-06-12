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
