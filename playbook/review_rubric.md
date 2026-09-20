# Review Rubric

How data review is conducted and reported in synthloop. The per-generator
specifics live in `data_projects/<name>/review_instructions/v*.md`; this file is
the invariant method.

Pass/fail uses the evaluation rubric pinned at the human checkpoint. Candidate
versions run in shadow and their findings stay visible, but never silently
replace the acceptance criterion. A high refutation kill-rate triggers
investigation of evidence and wording, not automatic weakening of any tier.

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
   instruction or supplied evidence needs diagnosis. Propose a candidate version
   with examples; retain the pinned evaluation version. Unresolved findings are
   not refuted: retain unresolved critical claims as blockers until resolved.

## Sampling

- Chunked review: start with 25-50 rows per reviewer; reduce by token budget so
  each row remains complete. Explicitly route a row that cannot fit.
- Stratified across: task category, turn type, score band (oversample
  sub-perfect), and outcome class (refusals, empty results, errors).
- At-scale corpora are re-sampled and re-reviewed; stage-3 verdicts do not
  transfer to stage-4 data.
- Validation gates use full-batch A/B review and row-level joint pass rates.
  Sampled reviews report reviewed denominators and uncertainty; unreviewed rows
  are unknown. At scale, use the approved sampling estimator, including weights
  for deliberate oversampling. Track cohort sample sizes alongside rates.
- Calibrate reviewer errors on human-labeled cases and keep a held-out set
  outside the repair loop. Review/refutation contexts are separate from the
  generator's rationale; independent contexts do not guarantee independent
  model errors, so compare against human calibration.

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
