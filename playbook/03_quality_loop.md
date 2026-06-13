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

Pass = all deterministic checks green AND no surviving critical findings AND
coverage within spec AND the raw-row read raises nothing new. Then go to the
human gate: present the summary, the examples, and the open questions. Human
approves -> stage 4. Anything else -> 3.4.

## 3.4 Repair: diagnose, then patch

- **Write the diagnosis first**: the mechanism of the failure, traced to root
  cause, reproduced offline if at all possible. "I added a filter that makes
  the symptom go away" is not a diagnosis.
- **Allowed without escalation**: prompt wording, steering lines, thresholds,
  keyword lists, sampling weights.
- **Requires diagnosis + new test**: anything in code - parsers, scoring,
  scheme rendering, state machines.
- **The ratchet**: every confirmed finding adds a deterministic guard
  (test, validation, counter alert) so this class cannot recur silently.
- **Gate-impact check**: if the repair adds or tightens a gate, compare
  accept-rate and inspect a sample of newly-rejected rows before keeping it.
- Version the change: bump generator version notes and, if reviewer behavior
  should change, write `review_instructions/v{n+1}.md`.
- Record diagnosis + change in `project_memory.md` (one paragraph each).

Then loop to 3.1.

## Exit criteria (human gate)

- Two consecutive passing cycles (one pass can be luck).
- Human has read the summary AND some raw rows, and explicitly approved
  scaling, recorded in `progress.md`.

## Common failure modes

- Trusting a passing judge: judges score rubric-consistency. Track C exists
  because a perfectly-scored batch can still teach the wrong lesson.
- Repair loops that oscillate: two prompt tweaks fighting each other across
  cycles. If the same metric flips twice, stop and diagnose.
- Reviewer findings taken at face value: without the refutation pass,
  plausible-but-wrong findings consume repair cycles.
