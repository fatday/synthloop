# Stage 3: The Quality Loop

**Purpose**: the loop you live in. Generate small, measure honestly, repair
with diagnosis, ratchet, repeat - until the batch passes the gates AND a
human reading the rows agrees it is what they want.

Inner-loop cadence should be minutes-to-an-hour per cycle. If a cycle costs
hours, the missing piece is almost always offline replayability (stage 2).

## 3.1 Small-scale generation

- Batch size: enough to measure the coverage spec (typically 500-5000; rare
  capabilities need enough rows to register). For a FIRST-EVER smoke of a new
  generator, start tiny (20-50) to catch crashes and format breaks cheaply,
  then go to the real size once it runs clean.
- Commit before generating (yes, even smokes).
- Record: batch id, commit, config, counts, into `progress.md`.

## 3.2 Automated QA (dual-track, every cycle)

**Track A - deterministic checks** (cheap, run first):
- Schema validation, required fields, format round-trips.
- Coverage histogram vs the design spec's numbers. Every capability counter
  above its floor. A zero where the spec expects usage is a HARD FAIL.
- Consistency backstops accumulated by the ratchet (see 3.4).
- Accept/reject rate vs previous batch (rejection-wall watch).

**Track B - agent review** (semantic):
- Chunk the batch (25-50 rows per reviewer) using the current
  `review_instructions/v*.md`.
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

Pass =
- accept-rate ≥ target, measured over the **FULL generated batch** (not the
  post-gate survivor set), AND
- **every baseline coverage cell ≥ its frozen floor** (a rise in accept-rate
  with any cell shrinking is a rejection-wall signal, not a pass), AND
- cumulative coverage **drift within budget** vs the frozen baseline, AND
- no surviving critical findings (scored with the rubric version **pinned to
  the last human checkpoint**, not one this loop edited), AND
- the raw-row read raises nothing new, AND
- this is a **clean cycle** — no code/constant/design edit was applied, so the
  reviewed rows came from current HEAD.

A pass reached autonomously is **provisional**: present summary, examples, the
coverage/drift table, and open questions to the human, whose review at the
checkpoint is the authoritative confirmation. Human approves → stage 4.
Anything else → 3.4. Never auto-scale.

## 3.4 Repair: diagnose, then patch (monotonic)

- **Write the diagnosis first**: the mechanism, traced to root cause,
  reproduced offline if at all possible. "I added a filter that makes the
  symptom go away" is not a diagnosis.
- **Autonomous (apply directly): fix the generator, or LOOSEN acceptance.**
  Prompt/steering wording, relaxing an over-strict threshold/keyword/gate,
  fixing a parser/scorer/schema so honest rows pass, raising a coverage
  weight/floor. Code changes get a minimal fix + a NEW test that **fails on the
  parent commit and passes on the fix** (a test that passes pre-fix is not a
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
  genuinely-bad. Cannot certify → present to the human, do not keep the fix.
- **Provenance**: commit + stamp the hash; the edit invalidates the prior
  commit's rows (do not count them); replay scoring/parsing/schema changes
  against retained prior rows and record a cutover if they would now re-label
  accepted rows. Reviewer-instruction edits are additive/tightening only.
- Record diagnosis + change + minor/major rationale in `project_memory.md`.

Then loop to 3.1.

## 3.5 Autonomous-loop guard rails (the basis for safe autonomy)

The loop may fix code, constants, and tune minor design without a human, but
only because these invariants make it impossible to narrow the data unseen.
They REPLACE the human code-reviewer between checkpoints; they are not optional.

1. **Frozen baseline.** Approved spec sections (goals/non-goals, schema,
   coverage categories + floors), the coverage histogram, and the target floor
   are frozen at each human checkpoint. The loop appends dated delta blocks and
   a HUMAN-DECISIONS ledger entry; it never edits frozen text. "Major" is always
   judged against the frozen baseline, never the accumulated deltas.
2. **Acceptance monotonicity.** Autonomous repair never net-tightens
   acceptance (see 3.4). Accept-rate is never improvable by losing coverage.
3. **Append-only judge & ratchet.** Reviewer rubric and ratchet tests are
   human-owned: additive/tightening edits only; relaxations are human-gated.
   The pass test is scored on the pinned rubric. Tier-1 critical definitions are
   pinned to the last checkpoint and exempt from kill-rate-driven loosening
   (that lever applies to Tier-2/3 only).
4. **Provenance: clean-cycle-to-pass.** Edits invalidate prior rows and are
   committed; new tests fail-on-parent/pass-on-fix; a cycle that edited anything
   cannot pass. At loop entry record the rollback anchor (last human-approved
   commit); every STOP reports HEAD + anchor + the autonomous commits made.
5. **Repair, not expand.** Autonomy restores quality on the approved surface;
   scope expansion and creative direction are proposed and surfaced at the
   checkpoint, applied only with explicit human direction. A cumulative drift
   budget (TV-distance vs baseline, default 0.20, or > 3 net-new autonomous
   subtypes) forces a hard gate even when each step looked minor.

`target-pass-rate` has a human-set floor in the spec; the loop may not run below
it, and lowering the floor is a hard gate. A STOP-to-diagnose may resume only if
the resolution is a generator/data fix; if the only way forward is to weaken a
gate/threshold/rubric/test, the loop stays stopped and presents to the human.

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
- Repair loops that oscillate: two tweaks fighting across cycles. If the same
  metric flips twice, stop and diagnose.
- Reviewer findings taken at face value: without the refutation pass,
  plausible-but-wrong findings consume repair cycles.
