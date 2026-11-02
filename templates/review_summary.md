# Review Summary — <generator> v<N>

> One durable artifact per reviewed batch. Written at the end of every
> `/review` (and the `/cycle` Review step) into
> `data_projects/<name>/reviews/v<N>.md`. Human-readable first: someone who
> was not in the loop should understand, from this file alone, how the batch
> went and exactly what is wrong with which rows. Evidence is verbatim, never
> truncated. Fill EVERY section; write "none" where empty.

## Verdict

- **PASS / FAIL / NEEDS-HUMAN**: <one word + one sentence why>. PASS requires
  **BOTH tracks ≥ target, independently** (not combined).
- **Track-B (LLM) pass-rate (accepted rows)**: <x.x%> (n=<n>, 95% <lo>–<hi>) vs target <95%>  — **worst cohort**: <cohort> <x.x%> (n=<n>, 95% <lo>–<hi>)
- **Track-A (deterministic) pass-rate (accepted rows)**: <x.x%> (n=<n>, 95% <lo>–<hi>) vs target <95%>  — **worst cohort**: <cohort> <x.x%>
- **Pass within noise?** <yes/no> (yes when an interval reaches below the target; the gate is unchanged, the human sees it is marginal)
- **Change vs v<N-1>**: <+/-x.x pts>; noise band <±y pts> (sampling interval of the difference plus reviewer spread) → <beyond noise / within noise>
- **Lever class this round**: <class>; null rounds in a row for this class: <k> (2 → plateau stop, `03_quality_loop.md` §3.3)
- **Both ≥ target?** <✅/❌>  (this is the pass test — each track on its own)
- **Reviewed**: <N> rows (<stratification, e.g. cap per mode×backend, oversampled weak cohorts>)
- **Commit / working-tree**: <hash or branch+state>   **Rubric scored against**: review_instructions/v<k>.md (pinned at last human checkpoint)
- **Refutation kill-rate**: <confirmed>/<raised> findings survived (<y> false positives dropped)

## Per-row problems (confirmed, post-refutation)

> Every row with a surviving (refutation-confirmed) problem. Sorted by severity
> then cohort. `row` = the row's stable id (seed) AND its line index in the
> reviewed file, so it can be pulled with the project's raw-row reader. One row
> may appear on multiple lines if it has multiple distinct problems.

| row (seed / #) | generator | mode / backend | severity | problem | detail |
|---|---|---|---|---|---|
| <seed> / <#> | <generator> | <mode> / <backend> | T1 | <label> | <one-line specific detail: what the row does wrong, with the offending value> |
| … | | | | | |

**Severity key**: `T1` = Tier-1 / critical (disqualifies the row); `T2` = quality
drag (counts against the dimension score but not auto-fail). **Problem labels**
(controlled vocabulary — extend per generator, keep stable): `deny_after_retrieval`,
`fabrication`, `ungrounded_answer`, `avoidable_abstention`, `format`,
`unadvertised_tool`, `missing_arg`, `coverage_gap`, `robotic_phrasing`, `other`.

## Problem tally (by label × severity)

| label | T1 | T2 | total | Δ vs v<N-1> |
|---|---|---|---|---|
| <label> | <n> | <n> | <n> | <+/-n> |
| **all** | | | | |

## Per-generator pass-rate — deterministic AND LLM (both must clear)

> Both QA tracks reported SEPARATELY on the same reviewed rows, grouped by the
> row's `generator` (the sub-generator that produced it). PASS rule: a generator
> passes only when **det pass ≥ target AND LLM pass ≥ target** — the two are NOT
> merged into one number; each must clear independently. **det** = Track-A
> deterministic check (conservative FLOOR — reads high, overstates quality).
> **LLM** = Track-B reviewer Tier-1 verdict. `top problem` = most common finding
> label.

| generator | reviewed | det pass | LLM pass (95% interval) | both≥target? | T1 | deny-after-retr | avoidable | top problem |
|---|---|---|---|---|---|---|---|---|
| <generator> | <n> | <d>/<n> | <l>/<n> (<lo>–<hi>) | <✅/❌> | <t1> | <deny> | <avoid> | <label (n)> |
| **ALL** | <n> | <det%> | <llm%> (<lo>–<hi>) | <✅/❌> | <t1> | — | — | — |

## Per-chunk pass-rate

> One reviewer per chunk — a quick check that no single reviewer is an outlier
> (a lone low/high chunk can signal reviewer drift rather than a data problem).

| chunk | pass | rate |
|---|---|---|
| <n> | <p>/<t> | <x.x%> |

## Track-A sweep digest

- **Structural invariants**: <OK / list HARD_FAILs>
- **Quality signals** (reported, not gated):

| signal | this batch | v<N-1> |
|---|---|---|
| correct (answered, grounded) | <x%> | <x%> |
| deny_after_retrieval | <x%> | <x%> |
| fabricated / ungrounded | <x%> | <x%> |
| avoidable-empty abstention | <x%> | <x%> |
| justified abstention | <x%> | <x%> |

## Coverage & yield deltas (vs v<N-1>)

- **Accept-rate** (full batch, NOT the pass bar): <x%>  (prev <x%>)
- **Per-cohort accepted volume vs floor**: <all ≥ floor / list shortfalls>
- **Cumulative drift vs frozen baseline**: <within budget / over by …>

## Systemic findings (not row-specific)

- <pattern the reviewers/refuter flagged across many rows — root cause if known>

## What was checked and is clean

- <invariants/dimensions that held — so a reader knows the absence of a finding
  is a real check, not an un-looked-at gap>

## Next action

- <the single next action — fix scope per finding, or the human-gate ask. Mirror
  this into progress.md's cursor.>
