# Review Instruction v<N>: <generator name>

> Versioned: copy to `review_instructions/v<N+1>.md` when reviewer behavior
> should change (new failure class found, new capability added). Reviewers
> always use the latest version; the version used is recorded per batch.

## What this data is

- One paragraph: the skill being taught, the format, what a good row does.

## Tier 1 - critical failures (any one fails the row)

> Start from playbook/review_rubric.md Tier 1 and add generator-specific
> classes discovered by the ratchet. Keep ids stable (T1.1, T1.2, ...).

- T1.1 ...

## Tier 2 - scored dimensions

| Dim | Question | Scale + anchors |
| --- | --- | --- |
| A |  |  |

## What does NOT count against a row

> Explicit, to prevent manufactured findings. Example: synthetic entity
> names are expected; flag unsound reasoning about them, not their existence.

-

## Evidence requirements

- Cite row id + verbatim offending content for every finding.
- You receive full rows; if anything appears truncated, report THAT, do not
  review around it.
- Your findings will face a refutation pass; only report what you can defend
  from the row itself.

## Changelog

- v<N>: <what changed and which incident motivated it>
