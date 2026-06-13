# Stage 1: Design

**Purpose**: produce a design spec a human can approve and an agent can
implement without re-deciding anything fundamental. The spec is a contract;
implementation surprises mean the spec was incomplete.

## Checklist

- [ ] **Goals and non-goals**: the skill(s) the data teaches, in one
      paragraph; what this generator deliberately does not cover.
- [ ] **Sample schema**: every output field, with one fully-worked example
      row, byte-exact in the target training format.
- [ ] **Generation architecture**: stages/states, which LLM calls happen
      where, what is deterministic vs sampled, how randomness is seeded.
- [ ] **Behavior coverage spec** (REQUIRED): the target distribution as
      numbers - task categories with weights, turn-type mix, difficulty mix,
      expected per-capability usage floor. This is what QA measures against.
- [ ] **Demand-side wiring**: for every capability in the coverage spec, what
      mechanism creates demand for it (steering lines, scenario seeds,
      weights)? Capabilities without a demand mechanism ship dark.
- [ ] **Quality rules**: what makes a row unacceptable (hard rejects) vs
      sub-par (scored). Which checks are deterministic vs judged.
- [ ] **External Reality Checks** (REQUIRED, answer all four):
      1. What external systems does generation touch, and what is the
         INDEPENDENT source of truth for each (a dashboard, a quota page, a
         dataset viewer the agent does not control)?
      2. What behavior-coverage telemetry proves every designed capability
         actually occurs? Name the counters.
      3. What is the provenance scheme (commit-before-launch, batch ids,
         row-level stamps)?
      4. What can only be observed at scale (rate limits, judge drift,
         rejection-rate creep), and how will it be watched?
      "None" is a permitted answer only with justification.
- [ ] **Offline replayability plan**: the deterministic twin/fixture for every
      external dependency, so the QA loop can run without live calls.
- [ ] **Review instruction v1**: instantiate `templates/review_instruction.md`
      for this generator (what reviewers check, what they ignore).
- [ ] **Open questions for the human**: collected explicitly, not buried.
      Interview the human only for what code and data cannot tell you (goals,
      taste, constraints, risk tolerance); answer everything else by reading
      the infra repo first, and batch the questions rather than drip them.
      Where you fill a spec value with your own choice, mark it `(proposed)`
      so the human can veto it cheaply at the gate.

## Output

`data_projects/<name>/design_spec.md` complete, plus
`data_projects/<name>/review_instructions/v1.md`.

## Exit criteria (human gate)

- A human has read the spec and answered the open questions.
- The coverage spec has numbers, the Reality Checks have answers, and the
  schema has a worked example.
- Explicit human approval recorded in `progress.md`.

## Common failure modes

- Coverage described in adjectives ("diverse", "balanced") instead of numbers.
- Reality Checks skipped because "we will add monitoring later" (later means
  after the first silent failure).
- Designing a new component when an existing one needed one parameter.
