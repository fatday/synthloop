# Principles

The distilled rules. Each was paid for by a real production incident in some
data-generation effort; none is theoretical. When a rule and a deadline
conflict, the rule wins, because every one of these exists to prevent a
failure mode that costs more than the time it saves.

## 1. Read raw rows every cycle

Automated metrics measure rubric-consistency, not task-design correctness. A
judge can score a conversation 10/10 while the underlying task design is
broken (a planned-answerable question made unanswerable by a retrieval bug
reads, to a judge, as a graceful refusal). Every QA cycle includes a
stratified raw-row read: a few rows per task category, per turn type,
oversampling sub-perfect scores and refusals. The reader's question is not
"does this pass the rubric" but "is this what we actually want a model to
learn".

## 2. Diagnose, then patch — and repair monotonically

Unsupervised repair loops patch the symptom the reviewer measured. They add
filters and gates until pass-rate looks good while the data distribution
quietly narrows (the rejection-wall failure: a well-meaning validator that
silently rejects most honest samples). The defense is not "a human must touch
all code" — it is that **autonomous repair may only fix the generator or
LOOSEN acceptance, never net-tighten it.** Within that constraint the loop may
edit code, constants, and tune minor design, because it then cannot narrow the
data behind your back. Every fix requires a written root-cause diagnosis, the
minimal fix, and — for code — a new test that **fails on the pre-fix commit and
passes on the fix** (a test that passes pre-fix did not catch the bug). If you
cannot explain why the bug happened, you are not done diagnosing.

What stays a human gate, precisely because it can narrow the data or move the
target: **any net-tightening of acceptance** (a new/tightened gate, code that
rejects/drops/filters rows, down-weighting a capability below its floor),
**relaxing the judge** (a Tier-1 definition, what reviewers flag), **weakening
a ratchet test**, **scope expansion / creative direction**, and **major design
pivots**. The loop proposes these with evidence and stops; it never applies them
alone. Accept-rate is never improvable by losing coverage — the pass test is
anchored to a frozen coverage floor the loop cannot move (see #5, #9, and
`03_quality_loop.md` §3.3/§3.5).

## 3. The ratchet (append-only)

Every confirmed incident becomes a permanent deterministic check: a unit test,
a schema validation, a consistency backstop, a counter with an alert. Quality
must be monotonic. A bug class fixed without a guard will return.

The ratchet — and the eval/holdout harness — are **append-only for an
autonomous loop**: it may ADD guards, but may never weaken, skip, xfail,
delete, or narrow an existing test or its fixtures. A required change to an
existing ratchet is a human gate. Enforce it mechanically: diff the test files
each cycle and stop if any existing assertion or fixture was removed or
loosened. A newly-failing ratchet is made to pass by fixing the generator,
never by editing the test — otherwise the loop can silently disable the very
monotonicity guarantee that is the basis for trusting its autonomy.

## 4. Design for offline replayability

The single biggest determinant of iteration speed. Every external dependency
(live API, LLM call, clock, randomness) gets a deterministic offline twin:
seeded fakes, recorded fixtures, replay harnesses. This converts
day-cadence debugging (relaunch, wait for warmup, scan logs) into
minute-cadence debugging (replay the exact scoring/dispatch offline). If a
component cannot be exercised offline, that is a design defect to fix before
scale, not after.

## 5. Coverage is a spec, and capabilities ship with demand and a counter

Declare the target distribution at design time: task categories with weights,
turn-type mix, expected per-capability usage. Measure the actual histogram
every batch and alert on drift. Two corollaries learned the hard way:

- A new capability (tool, branch, behavior) does not get exercised just
  because it exists. It needs explicit demand-side wiring (steering the
  task/user simulator toward it) or it ships dark.
- "Did it actually fire?" is checked on the FIRST run with a usage counter,
  never retroactively via someone noticing a dashboard at zero.

## 6. Adversarial verification of review findings

Review agents manufacture findings, especially when given truncated evidence.
Two rules: (a) every reported finding survives a refutation pass where an
independent reviewer tries to disprove it against the full raw row; (b)
evidence in review reports is verbatim and complete - row IDs plus the actual
offending content, never paraphrases, never truncated context (truncation
itself manufactures false findings).

## 7. Provenance: commit before every launch

Every batch of generated data must be traceable to the exact code that
produced it. Commit (a WIP commit is fine) before every launch, smoke or
scale, and stamp rows or batch metadata with the commit hash. Mid-run hotfixes
create mixed-generation corpora; record the cutover timestamp so batches can
be split later. The question "which code wrote these rows" must always be
answerable.

## 8. Honest environments

Never write false claims about tool or environment behavior into generation
prompts ("retrying returns different results" when it does not). The model
being trained learns those claims as world knowledge. Prefer honest empty
results over fabrication; an honest "not found" is good training data, a
plausible fabrication is poison.

## 9. Quality gates must not become rejection walls

Every new gate changes the accepted distribution. When adding one, measure
accept-rate before and after, and inspect a sample of REJECTED items: if the
gate rejects mostly-good samples, it is destroying coverage to buy precision.

## 10. Human attention is for taste and independent verification

The human's comparative advantage: judging whether the data is what they
actually want, and verifying claims against sources the agent does not
control (provider dashboards, quotas, their own reading). Structure reports
to spend human attention there - lead with verdicts and concrete examples,
never demand they re-derive your analysis.

## 11. Artifacts serve the next decision

Write the documents that change what happens next: the design spec, the
diagnosis, the review verdict with examples, the progress ledger. Skip
completeness theater. A per-chunk report nobody reads is process debt.

## 12. Update the playbook in the same change

When a process failure is found (not just a code bug), the fix includes
updating this playbook or the templates. Playbooks rot in weeks otherwise,
and a rotted playbook is worse than none because it is trusted.
