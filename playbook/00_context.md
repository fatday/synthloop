# Stage 0: Context

**Purpose**: understand the domain, the target model, and prior art before
designing anything. Output feeds the Context section of the design spec.

## Checklist

- [ ] **Environment first**: read `data_projects/ENVIRONMENT.md` (infra,
      generator catalog, benchmark targets, external resources). Most of the
      questions below should be answered FROM it; research only what it does
      not cover, and write what you learn BACK into it (the catalog only
      stays useful if every project that learns something updates it).
- [ ] **Target**: what model consumes this data, in what training stage (SFT,
      preference, eval)? What exact serialization format does it train on
      (chat template, tool-call tokens, thinking format)? Get a verbatim
      example of one training row from an existing accepted dataset.
- [ ] **Existing data**: what datasets already cover adjacent skills? Sample
      and read 10-20 rows from each. Note formats, conventions, quality bars,
      and what is missing that motivates this generator.
- [ ] **Prior generators**: pick reference generators from the environment
      catalog and read the closest one end to end. Note its architecture
      (state machine, prompt chain), its QA gates, and its known failure
      modes. Reuse beats reinvention; the catalog's "reusable parts" column
      is the shopping list.
- [ ] **Domain constraints**: external systems involved (APIs, sandboxes,
      corpora), their costs, quotas, auth, and failure behaviors.
- [ ] **Benchmark alignment**: if this data targets a benchmark family, start
      from the environment file's benchmark-targets table (style, known
      format quirks), then read the benchmark's actual scoring code, not its
      README. Exact-match details (names, formats, ordering) determine data
      conventions.

## Output

Fill the `Context` section of `data_projects/<name>/design_spec.md`: target format
(with the verbatim example), adjacent datasets, reused components, external
dependencies, and open unknowns.

## Exit criteria

- The target training format is pinned with a concrete example, not described
  from memory.
- At least one existing generator or dataset has been read, and the spec says
  what is reused from it.

## Common failure modes

- Designing against an imagined format and discovering the real chat template
  late (every prompt and parser changes).
- Ignoring an adjacent dataset and producing near-duplicate coverage.
