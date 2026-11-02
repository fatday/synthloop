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
- Preflight the whole launch chain offline, IN THE VENV THAT WILL RUN THE JOB,
  and keep it as a script the loop runs before every launch: every runtime
  module imports, the manifest resolves each arm, every registered state
  handler binds the runner's call shape, the first prompt builds, the ENGINE
  the recipe names is constructed, and a real tool call dispatches. A green
  unit suite is not this: it runs in the dev environment and never builds the
  engine. Borrowed environments are the sharp edge — when a shared venv or
  runtime moves, the generator can still import while the engine cannot.
- Watch the first ~10 minutes for failure signatures (exception / death counts
  vs the previous batch's whole wall), not only for job completion.
- Record: batch id, commit, config, counts, into `progress.md`.
- For throughput work, trace what each counter actually increments before calling
  it a model request: state advances can include no-model transitions. Count
  scheduled model queries and skipped states separately. Distinguish persisted
  rows, periodic worker checkpoints, and completed trajectories at the wall;
  use the same denominator and allocated worker-hours for comparisons.

## 3.2 Automated QA (dual-track, every cycle)

**Track A - deterministic checks** (cheap, run first). These are the
accept-time gates AND a **post-data sweep over the LANDED batch** — a script that
re-derives the deterministic signals from the data we actually collected, run
before the expensive Track B. Two output classes, kept strictly separate:

- **Structural invariants → HARD FAIL** (definitionally bugs that must never
  reach data; non-zero exit):
  - Schema validation, required fields, format round-trips (every tool call /
    tool result parses in the row's own emitted format).
  - Coverage histogram vs the design spec's numbers. Every capability counter
    above its floor. A zero where the spec expects usage is a HARD FAIL.
  - Provenance/wiring invariants: every tool the model *called* is one it was
    *advertised* (catches prompt/tool-name drift); required args present.
  - Consistency backstops accumulated by the ratchet (see 3.4) — each confirmed
    incident becomes a deterministic check here.
- **Quality signals → REPORTED, never gated here** (counts/rates that inform
  Track B and the human): grounding/fabrication rates, "denied-after-retrieval"
  / contradiction counts, abstention accounting (justified vs avoidable),
  duplicates, degenerate rows. Accept/reject rate vs previous batch
  (rejection-wall watch) lives here too.

> The post-data sweep is **read-only measurement**. It MUST NOT silently become
> an acceptance gate — turning a reported quality signal into a hard reject
> net-tightens acceptance, which is human-gated (see 3.5 and CLAUDE.md). The
> sweep reads each row from the row itself (no coupling to the generator
> codebase) so it stays runnable on any landed batch. Build it once per
> generator (e.g. `scripts/track_a_checks.py` in the project folder); the
> structural HARD FAILs are the standing regression net for the whole incident
> history, and the quality signals are a cheap pre-read that often confirms (or
> refutes) a fix before Track B spends tokens.

**Track B - agent review** (semantic):
- Chunk the batch (25-50 rows per reviewer) using the current
  `review_instructions/v*.md`.
- Reviewers must cite row ids and verbatim offending content.
- Verify substantive reading from model-visible tool output when review results
  depend on complete rows. Loading a file into a script, printing excerpts, or
  checking that a quote exists does not establish that the reviewer saw the
  persona, rules, dialogue, and tool results. Preserve and invalidate incomplete
  passes; rerun the required reading with bounded, untruncated outputs. A claimed
  second pass does not repair an unseen first pass.
- Initialize review checkpoints empty. Before appending each judged row, validate
  its complete visible-source receipt, source identity, and exact quotations.
  Reject unread placeholders, including default passing grades; a metadata census
  is not a review checkpoint. If a reviewer ends early, resume the remaining
  assignment without treating the partial report as complete.
- **Efficient evidence delivery**: when a complete row fits the explicit inner
  and outer output budgets, deliver all of its unchanged evidence frames in one
  model interaction. Verify exact, untruncated delivery; use bounded parts when
  necessary. A worker can save its personally authored single-row judgment,
  validate it, and fetch the next source in one tool cycle. Continue to the next
  row after each checkpoint instead of returning to the coordinator for each row.
  Batch source transport and bookkeeping, never default or copied judgments.
- Schedule the required frozen-control readings alongside raw review, and start
  independent refutation as soon as a raw chunk is frozen. Preserve required
  control counts, sources, phase separation and reviewer independence.
- Check source coverage and judgment-generation integrity while workers are
  active, so a compromised attempt is caught before a full chunk is wasted.
  Publish completed batch findings promptly with remaining phases clearly marked
  pending; claim full method completion only after every required phase passes.
- Record review wall time, model interactions, partial returns and discarded
  attempts separately. Measure the effect of a faster delivery path before
  claiming a speedup; source delivery alone does not prove comprehension.
- **Refutation pass**: an independent reviewer attempts to disprove each
  finding against the full raw row. Only surviving findings are reported.
- **Control chunk (instrument calibration)**: every cycle, one reviewer
  re-reviews a FROZEN anchor set (~50 rows from a pinned earlier batch) with
  the cycle's exact prompt and model. Report the headline beside the control
  and treat a headline move that the control also makes as instrument drift,
  not generator change. A pinned rubric does not pin the reviewer: a pass
  rate can move by tens of points when only the reviewer instance changes.
- Aggregate into one summary: verdict, confirmed findings with examples,
  score distribution, coverage notes, control-chunk delta.

**Track C - raw-row read** (the one that catches what A and B cannot):
- Stratified sample: a few rows per task category and turn type, oversample
  sub-perfect scores and refusals/empty-results.
- Question: "is this what we want a model to learn", not "does it pass".
- The human does some of this reading at least once per generator version;
  agents do it every cycle.

## 3.3 Pass gate

**Pass is a QUALITY bar, not a yield bar.** The accept-rate (fraction of
generation attempts that clear the deterministic gates) is NOT the pass
criterion: the gates legitimately reject imperfect attempts, so yield runs well
below target and chasing it would only mean loosening real gates. Track and
report accept-rate; never pass on it.

Pass = a **TWO-TRACK AND** — BOTH of the following pass-rates clear target
(default 0.95), each measured and thresholded INDEPENDENTLY (do NOT collapse them
into one "combined"/per-row-intersection number; each track must clear the bar on
its own, worst-cohort):
- **Track-B reviewer (LLM) pass-rate on ACCEPTED rows ≥ target** — ≥95% of the
  rows that cleared the gates are good training data, scored with the reviewer
  rubric **pinned to the last human checkpoint** (not one this loop edited), AND
- **Track-A deterministic-check pass-rate on ACCEPTED rows ≥ target** — the
  post-data sweep's per-row verdict (no false-denial / fabrication / leak /
  structural fail) clears target too. The deterministic track is a CONSERVATIVE
  FLOOR: it can read well above target (it only catches unambiguous, exact-match
  defects) while the LLM track is still failing on semantic/wrong-scope variants —
  so a high deterministic number NEVER substitutes for the LLM track, and vice
  versa. Both are required precisely because they catch different misses, AND
- **every baseline coverage cell ≥ its frozen floor** — this is what stops the
  loop from *gaming the quality bar by shedding hard rows* (tighten gates →
  accept only the easy rows → 95% "quality" on a narrowed set). Combined with
  acceptance monotonicity (§3.5 #2 — no autonomous net-tightening), quality
  cannot be bought by cherry-picking, AND
- cumulative coverage **drift within budget** vs the frozen baseline, AND
- no surviving critical findings, AND
- the raw-row read (Track C) raises nothing new, AND
- this is a **clean cycle** — no code/constant/design edit was applied, so the
  reviewed rows came from current HEAD.

A pass reached autonomously is **provisional**: present summary, examples, the
coverage/drift table, and open questions to the human, whose review at the
checkpoint is the authoritative confirmation. Human approves → stage 4.
Anything else → 3.4. Never auto-scale.

**The Track-B number is only comparable on a pinned instrument.** Reviewer
model, chunk size, and prompt are the instrument; changing any of them moves
the score by more than a repair round does. Pin all three across cycles, take
THREE readings of the FULL frozen control every cycle (a 10-row slice moves
10pp per row), and report **batch − its own control mean, with the control's
spread** beside the raw percentage. A raw Track-B delta across instruments is
not evidence of anything.

## 3.4 Repair: diagnose, then patch (monotonic)

- **Raise raw quality; never shed to pass.** Both pass-rates are cleared by making
  the generator produce better rows so the *whole accepted batch* qualifies — NOT
  by adding reject gates/filters or dropping hard rows to inflate the rate. A
  narrower dataset that scores high is strictly worse than an honest lower score on
  the full distribution. "The fix for a low pass-rate is a better generator, not
  fewer accepted rows." (Adding a reject is also net-tightening → human-gated, §3.5.)
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
- **A call-time contract must never refuse the ONLY exit from a seeded
  precondition.** Before shipping one, ask what the model must do to make
  progress from each seeded starting state (offline, logged out, no
  permission): if the contract can refuse that action, it livelocks the
  trajectory rather than retrying it. Check too whether the PROMPT already
  licenses what the contract refuses -- if it does, the model cannot win.
  Landed-row replay CANNOT catch either: it measures survivors, so a contract
  that prevents completion looks cheap. When the reviewed defect is "did it
  silently" rather than "did it at all", the fix belongs at answer time.
- **Read the fire list of the TOP families, not only the new guards'.** A high
  fire count is a DISAGREEMENT between the guard and the generator, and either
  side can be wrong: a top family can be a guard rejecting correct behaviour,
  for instance one put in the wrong by a newly added tool parameter. Compare a
  family's count against how often reviewers actually flagged that class, and
  after adding any tool parameter or field, grep the guards for the shape it
  may now collide with. Landed-row replay will NOT catch this: such guards show
  zero fires on landed rows because the retries eventually succeeded. The same
  collision hits the Track A sweep: a check keyed on field NAMES (an allowlist
  of "safe" keys, a "name field" heuristic) has never seen the new field and
  will fail every coherent row that carries it. Re-read every field-keyed check
  when the world gains a field, and adjudicate each structural fire by reading
  the row before reporting Track A as a count.
- **A prompt teach can remove a designed behaviour's supply.** Telling the
  user-sim to avoid one kind of phrasing can also stop it from using a
  neighbouring phrasing that a designed, guarded, checked axis depends on, and
  nothing fails. After every prompt teach, diff the designed-axis usage counters
  against the previous batch; a drop is a regression even when every check is
  green.
- **Anything identifier-shaped in a tool directory will be called.** A namespace
  index that describes capabilities as "<object> <verb>" phrases can lead the
  model to compose them into tool names -- a rise in unknown-name retries and in
  row loss, invisible in landed rows. A directory the model reads must list the
  callable names themselves, rendered exactly as the row renders them, and say
  that the directory entry is not callable; the rejection message must name the
  namespace and the load call so the retry can converge. Measure with a
  same-commit control arm on the old prompt: the cost can fall entirely on
  throughput while quality does not move.
- **A result-shape change must go through one emptiness predicate.** Replacing
  an empty list with an informative envelope (one that states a zero count) is a
  quality fix -- and every check that tests `result in ([], None)` reads the
  envelope as a hit and goes silent on exactly the rows it exists for. When a
  tool result changes shape, grep every consumer's shape test and route them
  through one shared predicate; replay the affected checks over the previous
  batch before and after to see the fire count move.
- **A retry cap is a budget for one reason, not a verdict on the answer.** A
  funnel that stops at the first firing check and, once that reason hits its
  cap, accepts the whole answer lets a capped false positive hide a real defect
  behind it. Let the capped reason step aside and keep evaluating; count the
  per-turn budget per attempt. And a check whose remedy is "run tool X" must
  fire in a state that can run X -- otherwise its retries are blind and the cap
  lands the defect.
- **Fix the world's vocabulary before the model's reading of it.** "next
  Tuesday" is read two ways by competent speakers. When the world must state a
  fact the model will later resolve (a day, a direction, a quantity), state it
  in the form with one reading (a date, a signed amount, a unit).
- **Measure before you detector**: replay every new guard/contract over the
  last landed batch and READ its fire list before shipping — the list gives the
  precision, the false-positive causes, and whether the defect is supply or
  model. A guard that fires many times more often than reviewers flagged its
  class is measuring something else.
- **The suite result is a claim about a quiescent tree.** Read the count line
  ("N passed, M failed"), never the exit code of a piped command; never gate on
  a `-x` run (it stops at the first failure and reads as green); edit nothing in
  the repo while a suite runs (tests that inspect source throw phantom errors);
  when other agents are editing sibling files, run the files that cover your
  change and the full suite only after they commit.
- **Classify every guard edit before writing it: loosen / predicate repair /
  rule change.** Loosenings and raw-quality fixes the loop applies. A *predicate
  repair* — an existing guard whose documented intent already covers the case
  and whose miss was a render or vocabulary bug (a regex blind to JSON-rendered
  calls, a word-boundary miss) — the loop applies too, but each one ships with
  its fire delta on the frozen rows in the commit message and the rulings list,
  so the human can veto. A *rule change* — removing an exemption, adding an
  intent, a new gate, or any Track-A relaxation — is propose-and-stop even when
  it corrects an obvious detector false positive. Two traps: a reviewer's
  "precision fix" can be a design REVERSAL that pinned tests already encode (run
  the pinned suites before believing the proposal), and a predicate repair can
  SURFACE hidden false positives (a rise in fires can read as "the guard works
  now" when some of the added fires are legitimate cases the guard does not know
  how to recognise) — replay every guard change over the frozen rows and read
  EVERY added key, never the aggregate.
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
- **A dead exemption manufactures a regression.** Every deterministic check has
  two kinds of branch: ones that FLAG a unit and ones that CLEAR it (the
  qualifier was stated, the real measurement was fetched, the claim was
  negated, the shape is out of scope). An exemption that never matches is
  invisible — the check still runs, still reports, and quietly routes every
  exempt unit into the violation count. So **print every exemption's count
  beside the violation count, and treat any exemption sitting at zero as a bug
  in the check until proven otherwise.** The usual cause is an exemption
  reading a different representation than the data has: structured records
  where the artifact stores rendered text, a field the producer renamed, a
  window one character too narrow. Two cheap habits catch it: hand-read the
  flagged units before believing the number (an exemption's own best example
  will be sitting in the flagged list, which is the tell), and make the check
  report its buckets as a partition that sums to the population.
- **Stopping a batch early raises its pass rate.** Rows land when whole conversations finish, so
  the first rows of a batch are the conversations that finish fastest: shorter and easier. A batch
  stopped once it reaches N rows therefore reads better than one run to the wall, with no change in
  the generator. Compare batches over the same landing window or the same full wall, never a stopped
  batch against a completed one, and report the pass rate by landing time beside the headline.
- **A stricter in-loop check can raise the pass rate by killing hard conversations, not by fixing
  them.** A check that sends more drafts back also drops more trajectories at its retry cap, and long
  conversations, with more turns to fail on, die first. The apparent gain can sit entirely in the strata
  where the deaths are. Planned length (or any stratum) must be recoverable for the dead trajectories
  too: draw it from the seed, and replay the draw from each death's logged seed. Credit a stricter check
  only for a gain within strata whose drops did not rise. Its offline false-fail rate does not predict
  this; only the live drops by stratum do.
- **A resumable runner must re-run the requests that failed in transport.** A batch job that records
  each request's outcome and skips recorded ones on restart will, if it records a connection failure as
  an outcome, come back from a preemption "complete" with those requests silently empty, and a
  completeness check that counts records instead of successful results will pass it. Drop failed
  records on resume, and count successes.
- **A behaviour you notice for the first time is not a new behaviour.** Before
  attributing anything in a batch to the change you just made, run the SAME
  instrument over the pre-change batch. Reading raw rows surfaces habits that
  were always there, and a fresh detector finds them on its first run, so the
  discovery date looks like an onset date. Wrong attributions of this kind
  include a "regression" that is a dead exemption in the detector; a repetitive
  habit blamed on the new prompt wording that the old batch shows at an
  identical ratio; and a rise that is the same content re-punctuated. The
  baseline run is cheap and it can change the conclusion, so it comes before the
  write-up, not after a challenge. Measure the thing form-independently too: a
  count keyed on one surface form (a standalone sentence, a specific phrasing)
  moves when the form moves even though the content did not.
- **Split a check's residual by what the reader must do about it.** When the
  survivors of a check are a mix of "restates what was asked" and "asserts
  something unsupported", one number hides the second inside the first. Report
  the sub-buckets and sort the ones that need reading first; a headline that
  stays comparable across batches and a residual a human can act on are
  different jobs.
- **A model swap is a new engine contract; probe every fixed-budget sub-call
  shape against the live server before the launch.** Sub-calls that expect a
  short verdict (a judge checklist, a one-line verifier) carry small completion
  budgets tuned for the previous model. A model with native reasoning spends
  that budget inside its reasoning, the server returns the reasoning and no
  content, the engine hands the caller `None`, and the trajectory dies with an
  empty reason at the most expensive possible moment — after the whole
  conversation was generated. One request per sub-call shape, sent to the live
  server before the launch, reads `finish_reason`, completion tokens and whether
  content exists; it costs far less than a wasted launch. Treat a `None`
  completion as a retryable request, never a trajectory death, and put the count
  of such completions in every death census (they carry no reason, so a census
  keyed on reasons cannot see them).
- **Size the batch by per-trajectory latency, not by aggregate throughput.** A
  row lands only when its whole trajectory finishes, so in a fixed wall the
  question is whether `queries per row × seconds per query per slot` fits the
  wall, not how many tokens per second the server reports. In a prefill-bound
  regime (long prompts, no prefix reuse), raising concurrency can raise
  aggregate query throughput only a little while it multiplies every
  trajectory's latency, until nothing would land before the wall. Read the
  runner's per-trajectory progress (queries so far, per worker) at ten and
  twenty minutes and extrapolate; a server line showing an empty queue and spare
  KV cache describes the decoder's headroom and says nothing about how long each
  trajectory takes.
- **A per-row flag is not shipped until a landed row shows both of its values.**
  A/B arms, augmentation draws and usage counters live on the generator object,
  and the parent's sample-completion step may reset that object before the child
  writes its metadata. Unit tests can cover the draw and the prompt text of an
  A/B while none reads a row, and every row records the control arm. Before the
  smoke, run the offline end-to-end dry run and assert the new flag appears with
  BOTH values in its landed metadata; measure a new usage counter on a batch
  that has the behaviour, because a counter keyed on a shape the model never
  produces reads as "never shipped" and sends the diagnosis the wrong way.
- **When the inner gate and the outer review disagree, look for the ground
  truth the loop threw away.** Join the generator's own accept signal to the
  review's verdict row by row before theorising: an in-loop judge can score a
  batch's worst rows at the top of its scale when the defect is a figure that
  contradicts a field the row already contains. Such a judge cannot see it — an
  LLM asked for facts answers surface questions and defaults to fine on anything
  needing a cross-reference. The fix is not a better judge prompt but the check
  the pipeline lacks or has dropped. **Gate deterministically on whatever the
  environment can prove and ask the model or the judge only for taste.** Where a
  reply states a figure, bind it to a field: allow the value, its rounding and
  its unit conversions, and treat the rest as ungrounded.
- **A mandate you can express as a predicate should never be a prompt line.**
  Asking the model to confirm that every number in the reply is in a result or
  is marked as an estimate is such a mandate. The same requirement as code is a
  per-turn retry with a named number and a named field. Ask the model for what
  only it can do; compute the rest.
- **A check is only as good as what its evidence builder renders — measure the
  contents, never the emptiness.** A reader (an LLM judge, a pre-send verifier,
  a human reviewer) is shown a compacted view of what the run produced, and that
  compaction is where the defect hides. An evidence builder that keeps an
  allow-list of interesting field names can describe READ results well and
  ACTION results not at all: a record that reports a changed setting or an error
  holds no allow-listed key, so the whole record is dropped — the reader is
  shown the call and never its outcome. It then reports true statements as
  unsupported and pushes the model toward hedging, which shows up in the review
  as under-claiming. Two habits: **arm a check only after you have seen its
  inputs render** for the case it is meant to catch; and when the hypothesis is
  that something is MISSING from an artifact, measure the artifact's contents
  against what should be in it — counting how often the artifact is *empty*
  tests a different, much rarer failure, and passing that test is how the real
  one survives.
- **Pin the consumed artifact, not the accounting beside it.** A coverage bundle
  can declare a multi-call plan and a test can assert that plan while the
  capability still reads zero: the plan is accounting, while the thing the model
  actually reads is the directive — and the directive can ask for fewer steps
  than the plan declares and then forbid extras. Any time a plan, a manifest or
  a counter describes what a prompt is supposed to demand, assert it against the
  RENDERED prompt; a test over the accounting passes in exactly the world where
  the supply is broken.
- **A signal needs its denominator in the same table as the numerator.** A sweep
  can print `axis:<name>: <n>` for an axis that armed many times and took effect
  only <n> times — the armed count living in a different report. The review and
  the next reader then take <n> for the arming and write off the axis as never
  drawn. Emit the pair (`armed` beside `took effect`); a lone integer will be
  read as whichever of the two the reader was already thinking about.
- **A widening change is measured by what the artifact now holds in TOTAL, never by
  the delta you intended.** A fix that makes action results render can also make every
  node of a fetched tool definition render, because a recursive record walk yields the
  envelope, the function descriptor and one dict per parameter. A validation replay that
  checks only what the change set out to add will confirm it and ask nothing else, so the
  batch can launch with most of every rendered record being a tool definition — the
  directory crowding the world out of a small slice. The live check that catches this is
  reading the consumer's own complaints, such as verifier notes that keep saying the
  evidence contains only tool definitions. Two habits: after widening what an artifact
  includes, **count its contents by SOURCE and look at the biggest contributor**, not at
  your own additions; and when a downstream reader keeps objecting in the same words,
  **read its objection as a measurement** rather than as noise to be tuned away.
- **A mandate that needs its own turn needs a plan slot, not better wording.** A directive can
  contain two kinds of clause: one that *modifies a turn the plan already allocated* (how a
  request is phrased) and one that *requires a turn the plan never allocated* (an extra kind
  of request). The user-sim's turns are filled by the conversation plan; a style directive can
  change how an allocated turn is phrased and cannot conjure a new one. **Before writing a
  mandate, ask whether it modifies existing behaviour or demands new behaviour — the second
  kind belongs in whatever allocates the work.**
- **Fixing a check's inputs is not evidence that the check pays.** An LLM verifier can turn out
  to be reading evidence that omits the action it was asked about; fixing that is real and
  measurable (its revision rate falls, its remaining notes are genuine cross-reference defects,
  and it stops repeating itself). A per-row A/B can still show that it moves the reviewer
  pass-rate by less than the noise band while costing throughput. Repairing a mechanism and
  justifying a mechanism are two different measurements, and the second one is the one that
  decides whether it ships.
- **Where the code already holds the mapping, key the check on it.** A check that asks
  "did this request ever search the store that owns the thing the user asked about?" can
  be written several ways: entity nouns matched against tool-name substrings; the same
  thing bound to the user's own request; or a family map built on the tool registry's
  namespace→tools table. The registry knows which family a tool belongs to and no
  substring ever can. Before inventing a lookup table for a check, look for the one the
  system already ships.
