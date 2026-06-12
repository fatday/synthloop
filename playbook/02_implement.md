# Stage 2: Implement

**Purpose**: build the generator to the spec, with the offline-replay and
telemetry hooks that make the quality loop fast. The hooks are not optional
extras; they ARE the iteration speed.

## Checklist

- [ ] **Generator code** per the design spec, in the user's codebase,
      following its conventions (style, imports, registration).
- [ ] **Offline twins first-class**: every external dependency has its
      deterministic twin (seeded fake, recorded fixture) wired through the
      same code path as the live version, switchable by config. The QA loop
      must be able to run with zero external calls.
- [ ] **Telemetry counters**: per-capability usage counts emitted with each
      batch (or derivable from row metadata in one cheap scan). Implement the
      counters named in the design spec's Reality Checks.
- [ ] **Provenance stamps**: rows or batch metadata carry the code commit and
      a batch identifier.
- [ ] **Unit tests for the seams**: schema rendering/validation, the
      deterministic twins (same seed, same output), parser round-trips, and
      any scoring/ranking logic (testable offline by construction).
- [ ] **Operational scripts**: launch wrappers, row counters, coverage
      tallies, upload/processing tools go in
      `data_projects/<name>/scripts/` (NOT the infra repo, NOT new ad-hoc
      folders). They run against the infra repo's environment; the runbook
      records how.
- [ ] **Runbook**: the exact commands to smoke-generate, count rows, tally
      coverage, and run the test suite, written into `progress.md`.

## Output

Working generator + tests green + runbook recorded.

## Exit criteria

- An end-to-end micro-run (5-20 samples) completes; rows validate against the
  schema; the coverage tally script runs and reports.
- The full loop (generate, tally, review-sample) can run offline.
- Code committed (provenance starts now, not at scale).

## Common failure modes

- Skipping the offline twin "to save time": every later bug now costs a live
  run to reproduce.
- Schema details that silently differ between the prompt-facing rendering and
  the validator (type unions, optional handling, casing). Test the rendered
  schema explicitly - this class of bug blocks capabilities silently.
- Building telemetry "after we see it works": dark capabilities are invisible
  precisely until telemetry exists.
