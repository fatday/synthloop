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
   disprove it. Only surviving findings reach the report. Track the
   refutation kill-rate: a high share of findings refuted means the review
   instruction is too loose and is manufacturing noise - tighten it (next
   `review_instructions/v*.md`) so reviewers stop raising what the rows do
   not support.

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

One durable summary per batch, written to `reviews/v<N>.md` from
`templates/review_summary.md` (not just reported in chat — it is the human's
scannable record of every iteration). It contains:
- Verdict line first (pass / fail and why, one sentence) + Track-B pass-rate vs
  target and the worst cohort.
- **Per-row problem table**: one line per confirmed (post-refutation) row-level
  finding — row stable id (seed) + line index, generator, mode/backend cohort,
  severity (T1/T2), problem label (controlled vocabulary), and a one-line detail
  with the offending value. This makes "what is wrong with which row" directly
  scannable, not buried in prose. A problem tally (label × severity, Δ vs prior
  version) sits beside it.
- Confirmed findings narrative: verbatim evidence + suspected mechanism, grouped
  by class, ordered by severity (the table's detail column links to these).
- Track-A sweep digest, score/coverage distributions vs the spec, and
  coverage/yield deltas vs the prior version.
- What was checked and found clean (so absence of findings is informative).
- Open questions for the human, separated from findings, + the single next action.
