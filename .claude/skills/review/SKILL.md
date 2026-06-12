---
name: review
description: Run the dual-track QA review on the latest batch of a generator project - deterministic checks, chunked agent review with refutation pass, raw-row read, and a verdict. Usage - /review <generator-name>
---

# /review <generator-name>

1. Read `data_projects/<name>/progress.md`, the design spec's coverage numbers,
   and the LATEST `review_instructions/v*.md`. Read
   `playbook/03_quality_loop.md` section 3.2 and `playbook/review_rubric.md`.
2. **Track A - deterministic**: schema validation, coverage histogram vs the
   spec's numbers, capability counters vs floors, ratchet checks,
   accept-rate vs previous batch.
3. **Track B - agent review**: chunk the batch 25-50 rows per reviewer with
   the current review instruction. Reviewers cite row ids + verbatim
   evidence and receive FULL rows (never truncate). Then run the refutation
   pass: an independent reviewer per finding, given the full row, tries to
   disprove it. Drop refuted findings; keep a count of how many died (a high
   refutation rate means the review instruction needs tightening).
4. **Track C - stratified raw read**: a few rows per category and turn type,
   oversampling sub-perfect scores, refusals, and empty results. Ask "is
   this what we want a model to learn".
5. Write ONE summary per `playbook/review_rubric.md` report format: verdict
   line first, confirmed findings with verbatim evidence, distributions vs
   spec, what was checked and clean, open questions.
6. Record the verdict in the batch ledger. If pass: present to the human for
   the gate. If fail: hand the confirmed findings to `/repair`.
