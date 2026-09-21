# Stage 3: The Quality Loop

**Purpose**: the loop you live in. Generate small, measure honestly, repair
with diagnosis, ratchet, repeat - until the batch passes the gates AND a
human reading the rows agrees it is what they want.

Inner-loop cadence should be minutes-to-an-hour per cycle. If a cycle costs
hours, the missing piece is almost always offline replayability (stage 2).

## 3.1 Small-scale generation

- Read `progress.md` and follow `recovery.md` before launch.
  Reconcile active jobs and incomplete reviews; never blindly regenerate.
- **Functional smoke**: 20-50 rows, with directed cases for every designed
  capability. This checks crashes, format and reachable paths; it is not a
  distribution estimate and cannot count as a clean validation pass.
- **Validation batch**: use the approved minimum total and per-cohort sample
  sizes, coverage floors, target and drift budget from the approved design spec.
  Typically 500-5000 rows; rare capabilities need more observations or directed
  tests. Under independent sampling, a 1% capability is absent in 50 rows about
  61% of the time. Zero observations in an undersized random sample means
  insufficient evidence, not proof of a broken capability.
- Commit before generating (yes, even smokes); verify a clean infra worktree.
- Reserve batch/job identity before submission. Retain the full raw batch and
  generated-row inventory BEFORE filtering, including rejected rows. Record
  failed attempts, retries and spend separately.
- Record code/framework commits, model, seed and input versions in the batch
  metadata or progress.md. Keep job handles and review progress there too.

## 3.2 Automated QA (dual-track, every cycle)

**Track A - deterministic checks** (cheap, run first):
- Schema validation, required fields, format round-trips over ALL emitted rows,
  including rejects, not just accepted survivors.
- Coverage histogram vs frozen floors and minimum sample sizes. A directed
  capability test that cannot fire is a failure. An undersized random sample
  needs more evidence; a sufficiently sized batch below a floor fails validation.
- Consistency backstops accumulated by the ratchet (see 3.4).
- Accept/reject rate vs previous batch (rejection-wall watch).

**Track B - agent review** (semantic):
- Chunk the full validation batch using the pinned evaluation rubric. Start
  with 25-50 rows per reviewer, reducing chunk size to fit full rows within the
  context budget. Never truncate a row; route oversized rows explicitly.
- Persist planned/completed chunk IDs and evidence. Reviewers receive the task
  spec and raw rows in a separate context, without the generator's repair
  rationale. Refuters see the claim and full row, not a desired outcome.
- New review instructions are candidate versions evaluated in shadow mode until
  a human checkpoint adopts them. Discovery findings remain visible even when
  the pinned rubric does not yet cover the class; new raw-row concerns block pass.
- Reviewers must cite row ids and verbatim offending content.
- **Refutation pass**: an independent reviewer attempts to disprove each
  finding against the full raw row. Only surviving findings are reported.
- Aggregate into one summary: verdict, confirmed findings with examples,
  score distribution, coverage notes.

**Track C - raw-row read** (the one that catches what A and B cannot):
- Stratified sample: a few rows per task category and turn type, oversample
  sub-perfect scores and refusals/empty-results.
- Question: "is this what we want a model to learn", not "does it pass".
- The human does some of this reading at least once per generator version;
  agents do it every cycle.

## 3.3 Pass gate

Pass is **not** "accept-rate ≥ target". A loop optimizing accept-rate can hit
target by *cheating* — rejecting honest-but-imperfect rows, shedding a hard
capability — so the pass test is anchored to a coverage floor that the loop
cannot move:

Define N as all emitted rows, including rejects. Always report A_pass/N,
B_pass/B_reviewed, reviewed sample size, and (for full review) joint_pass/N.
A and B each passing 95% is not enough: disjoint failures can leave joint pass
at 90%. Unreviewed B rows are unknown, never assumed good. At-scale sampled
reviews report the approved sampling estimator and uncertainty separately;
they do not establish a full-batch validation pass.

A clean validation pass requires all of:
- Full Track-A and Track-B review, with **joint_pass/N >= target**, AND
- every cohort has sufficient observations, joint rate >= target, and joint
  accepted count >= its frozen floor, AND
- cumulative total-variation distance of accepted cohort shares vs the frozen
  baseline is within the approved budget, AND
- no surviving critical findings under the pinned evaluation rubric, AND
- refutation, ratchets and the raw-row read are complete with no new concerns, AND
- no code/config/prompt/design edit during the cycle; the rows match current
  committed code and pinned inputs.

Record the verdict and evidence in the review summary and progress.md.
The first clean pass requests an independent confirmation batch (new seed, same
code/config/rubric/model/baseline). The second
consecutive clean pass stops for human review. A failed/edited cycle resets the
streak; changes to code, behavior config, model, rubric or baseline require
fresh validation. Duplicate batches or repeated seeds cannot satisfy two passes.
Human approval is bound to the concrete scale plan, not just a generic pass.
Never auto-scale.

## 3.4 Repair: diagnose, then patch (monotonic)

- **Write the diagnosis first**: the mechanism, traced to root cause,
  reproduced offline if at all possible. "I added a filter that makes the
  symptom go away" is not a diagnosis.
- **Autonomous (apply directly): fix the generator, or LOOSEN acceptance.**
  Prompt/steering wording, relaxing an over-strict threshold/keyword/gate,
  fixing a parser/scorer so honest rows pass, or improving demand-side
  steering within the approved surface and coverage budget. Frozen schema and
  floors do not change autonomously. Code changes get a minimal fix + a NEW test
  that **fails on the parent commit and passes on the fix** (a test that passes pre-fix is not a
  ratchet) + the suite. Minor design tuning is written to the spec's
  append-only AUTONOMOUS-DELTA section, never into frozen text.
- **Human-gated (propose + STOP, never apply autonomously): anything that
  net-tightens acceptance or moves a frozen reference.** A new/tightened gate;
  any code that rejects/drops/filters/fails rows; a down-weight pushing a
  baseline cell below floor; relaxing the judge (Tier-1 definition, what
  reviewers flag); weakening/skipping/deleting an existing ratchet test or
  fixture; scope expansion or a creative direction; a major design pivot. When
  minor-vs-major is unclear, escalate. Present diagnosis + before/after
  accept-rate + the verbatim newly-rejected sample.
- **The ratchet** (append-only): every confirmed finding adds a deterministic
  guard so the class cannot recur. The loop may add guards; it may never weaken
  one. Diff the test files each cycle and STOP if an existing assertion/fixture
  was removed or loosened.
- **Gate-impact check** (on the CODE path too, not just thresholds): any change
  that can reject/drop/filter/fail rows is a gate — compare accept-rate and
  per-cell coverage before vs after, read a verbatim sample of newly-rejected
  rows. A passing unit test is necessary but not sufficient; a net-tightening
  change is human-gated regardless of the test.
- **Adversarial verification of the fix**: an independent pass must try to show
  the fix raised accept-rate by excluding honest rows rather than improving the
  generator — read the newly-rejected rows verbatim and certify they are
  genuinely-bad. Use the SAME retained rows for before/after acceptance, not
  unrelated random batches. For newly accepted rows, require the pinned semantic
  checks too: loosening acceptance alone is not evidence of improved quality.
  Cannot certify → present to the human, do not keep the fix.
- **Provenance**: commit + stamp the hash; the edit invalidates the prior
  commit's rows (do not count them); replay scoring/parsing/schema changes
  against retained prior rows and record a cutover if they would now re-label
  accepted rows. Retain old rows for replay/audit; do not delete them. Candidate
  reviewer edits are additive/tightening only and do not replace the pinned
  evaluation rubric until an authorized checkpoint.
- Record diagnosis + change + minor/major rationale in `project_memory.md`.

Then loop to 3.1.

## 3.5 Autonomous-loop guard rails (the basis for safe autonomy)

The loop may fix code, constants, and tune minor design without a human inside
these constraints. The agent checks actual outputs and review evidence before
marking a cycle passed; a checklist completed without evidence is insufficient.

1. **Frozen baseline.** Approved spec sections (goals/non-goals, schema,
   coverage categories + floors), the coverage histogram, and the target floor
   are frozen at each human checkpoint. The loop appends dated delta blocks and
   a HUMAN-DECISIONS ledger entry; it never edits frozen text. "Major" is always
   judged against the frozen baseline, never the accumulated deltas.
2. **Acceptance monotonicity.** Autonomous repair never net-tightens
   acceptance (see 3.4). Accept-rate is never improvable by losing coverage.
3. **Append-only judge & ratchet.** Reviewer rubric and ratchet tests are
   human-owned: additive/tightening edits only; relaxations are human-gated.
   The pass test is scored on the pinned rubric. Any change that makes a real
   failure easier to pass, at any tier, requires human approval. A high refutation
   kill-rate prompts evidence/instruction diagnosis, not automatic relaxation.
4. **Provenance: clean-cycle-to-pass.** Edits invalidate prior rows and are
   committed; new tests fail-on-parent/pass-on-fix; a cycle that edited anything
   cannot pass. At loop entry record the rollback anchor (last human-approved
   commit); every STOP reports HEAD + anchor + the autonomous commits made.
5. **Repair, not expand.** Autonomy restores quality on the approved surface;
   scope expansion and creative direction are proposed and surfaced at the
   checkpoint, applied only with explicit human direction. A cumulative drift
   budget (TV-distance vs baseline, proposed default 0.20) forces a hard gate
   even when each step looked minor. New scope is proposed, not accumulated
   through autonomous additions.

`target-pass-rate` has a human-set floor in the spec; the loop may not run below
it, and lowering the floor is a hard gate. A STOP-to-diagnose may resume only if
the resolution is a generator/data fix; if the only way forward is to weaken a
gate/threshold/rubric/test, the loop stays stopped and presents to the human.

## 3.6 Stop, budget and recovery

Persist the cycle cursor after each sub-stage. Stop on a hard gate, confirmed
regression/oscillation, ratchet failure, unreconciled infrastructure failure, or
approved cycle/cost/time cap (proposed default: six validation cycles). A
transient failure can be retried only under the approved bounded retry policy,
after checking the existing job identity. Monitor in-flight spend too.

Every stop records the reason, current HEAD, rollback anchor, autonomous commits,
coverage/joint-rate deltas and one next action. Cancel the actual scheduled
wakeup/job when using a platform loop; a Markdown next-action change is not
cancellation. Follow `platforms.md` and `recovery.md`. Completion at the second
clean pass still requires human checkpoint review and separate scale approval.

## Exit criteria (human gate)

- Two consecutive **clean** passing cycles (one pass can be luck; a passing
  cycle that applied an edit does not count — see 3.5 #4).
- The human has read the summary AND some raw rows, ratified any autonomous
  AUTONOMOUS-DELTA spec entries, and explicitly approved scaling, recorded in
  `progress.md`. An unratified delta blocks scale.

## Common failure modes

- Trusting a passing judge: judges score rubric-consistency. Track C exists
  because a perfectly-scored batch can still teach the wrong lesson.
- **Reward-hacking the metric** (the reason 3.3/3.5 exist): an autonomous loop
  can reach target by narrowing coverage, suppressing findings, relaxing the
  rubric it is graded by, or weakening its own ratchet — every per-cycle check
  green, the human seeing only survivors. Monotonicity + frozen baseline +
  append-only judge/ratchet + clean-cycle-to-pass are the antidote; if any feels
  inconvenient mid-loop, that is the failure mode arriving, not an exception.
- Mistaking sampling noise for regression: a cell falling relative to the last
  random batch is not itself a stop condition. Check frozen floors, sample size,
  drift budget and paired replay. Recurrence of a confirmed defect or opposing
  fixes on matched evidence is an oscillation stop, not two noisy metric flips.
- Reviewer findings taken at face value: without the refutation pass,
  plausible-but-wrong findings consume repair cycles.
