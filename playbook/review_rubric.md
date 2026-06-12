# Review Rubric

How data review is conducted and reported in synthloop. The per-generator
specifics live in `data_projects/<name>/review_instructions/v*.md`; this file is
the invariant method.

## Structure: tiered review

- **Tier 1 - critical failures** (any one fails the row): wrong-fact
  grounding against the row's own context, fabricated tool results or
  capabilities, format violations that break training, leaked
  pipeline/harness language in model-visible text, reasoning that
  papers over a contradiction instead of addressing it.
- **Tier 2 - dimension scores**: per-generator dimensions defined in the
  review instructions (e.g. action correctness, argument fidelity, response
  naturalness). Each dimension gets a defined scale and anchors.
- **Tier 3 - holistic bonus**: coherence, naturalness, persona consistency.

What does NOT count against a row should be stated explicitly in the review
instructions (e.g. fabricated-but-plausible entity names in a synthetic world
where source realism is not the training target). Reviewers flag unsound
REASONING about sources, not the synthetic sources themselves.

## Evidence rules (hard requirements)

1. Every finding cites the row id AND quotes the offending content verbatim.
2. Reviewers receive FULL rows. Never truncate the context a reviewer sees:
   truncation manufactures false findings (a fact "missing" because it was
   cut, a "leak" that the full text justifies).
3. Findings are claims, not verdicts. Every finding goes through a
   refutation pass: an independent reviewer, given the full row, tries to
   disprove it. Only surviving findings reach the report.

## Sampling

- Chunked review: 25-50 rows per reviewer to keep attention honest.
- Stratified across: task category, turn type, score band (oversample
  sub-perfect), and outcome class (refusals, empty results, errors).
- At-scale corpora are re-sampled and re-reviewed; stage-3 verdicts do not
  transfer to stage-4 data.

## Judge-consistency backstop

When a numeric judge is part of the pipeline, add a deterministic
contradiction check: a top score whose written analysis admits a failure
(or arithmetically cannot produce that score under the rubric) is dropped,
not trusted. Judges drift; the backstop is cheap.

## Report format

One summary per batch:
- Verdict line first (pass / fail and why, one sentence).
- Confirmed findings: id + verbatim evidence + suspected mechanism, grouped
  by class, ordered by severity.
- Score and coverage distributions vs the design spec's numbers.
- What was checked and found clean (so absence of findings is informative).
- Open questions for the human, separated from findings.
