# Environment: <workspace name>

> Instantiate ONCE per workspace as `data_projects/ENVIRONMENT.md`. This is
> the shared context every generator project inherits: the infra you generate
> with, the generators worth copying, and the benchmark styles you target.
> Agents read this BEFORE any project work; keep it current, it is the
> difference between an agent that reuses your stack and one that reinvents it.

## 0. Workspace directories

> Filled by `/survey` (agents classify by inspection, humans confirm).
> Every accessible directory gets a row; "role" is one of: data-infra,
> benchmark, seed-corpus, vendored-reference, serving/infra, unknown.
> A confirmed data-infra row is REQUIRED before implementation work can
> start; all other roles are optional context.

| Path | Role | Evidence (what decided it) | Used for | Confirmed |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 1. Data generation infra

- **Framework / repo**: <where generator code lives, link/path>
- **Generator patterns**: <the base classes or architectures generators follow,
  e.g. single-step, state-machine multi-turn, read-transform-write; where to
  find the canonical example of each>
- **How to run**:
  - generate (small): `<command>`
  - generate (scale): `<command / scheduler notes>`
  - validate / lint / test: `<commands>`
- **Engines available**: <API models, local serving (vLLM etc.), which to use
  for what role (author, simulator, judge), cost notes>
- **Output format(s)**: <serialization, chat template, tool-call format, where
  the verbatim reference example lives>
- **Where data goes**: <output dirs, publishing target (hub/registry), naming
  and prefix conventions>
- **House conventions**: <style rules, language policy, review report rules,
  anything a fresh agent must not violate>

## 2. Generator catalog (references for reuse)

> One row per existing generator worth knowing. "Reusable parts" is the
> important column: the fastest path to a new generator is stealing the right
> components from an old one.

| Generator | Teaches | Architecture | Reusable parts | Known pitfalls |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 3. Benchmark / style targets

> One row per benchmark family or data style this workspace targets. The
> "format quirks" column prevents the classic failure: generating data that
> is right in spirit and wrong in the exact-match details.

| Target | What it measures | Format / prompt style | Format quirks that bite | Reference (scoring code, not README) |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 4. External resources

- **APIs / subscriptions**: <providers, which endpoints, quotas, where usage
  dashboards live (these are the independent sources of truth for Reality
  Checks)>
- **Seed datasets / corpora**: <name, location, what they are good for>
- **Compute**: <cluster/scheduler, partitions, known flakiness patterns and
  the standard remediations>

## 5. Cross-generator lessons

> Workspace-specific lessons that do not generalize enough for
> playbook/principles.md but apply to more than one generator here
> (e.g. "judge model X inflates scores on long conversations").

-
