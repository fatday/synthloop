# Platform adapters

The shared playbook defines verdicts and authorization. These adapters provide
entry points, independent review and scheduling; neither owns a separate policy.
Record the CLI version used in the project runbook. Capability-detect unsupported
features and use the documented fallback rather than silently skipping a check.

## Claude Code

Start in synthloop with `claude --add-dir /path/to/project-infra-worktree`.
The eight `.claude/skills/` commands load `workflows.md`. Review and refutation
can use `.claude/agents/sl-reviewer.md` and `sl-refuter.md` in separate contexts.
Supply the pinned spec/rubric and exact complete rows explicitly; do not assume
the subagent inherited your conversation. Their tools are read-only file tools;
the coordinator runs deterministic scripts and persists their reports.

`/cycle` can drive the bounded inner loop directly. `/loop /cycle <name>` is
optional. Save its scheduling handle with project state/run notes. On pass
checkpoint, hard gate or exhausted budget, cancel the pending wakeup using the
available scheduler tool. Current self-paced loops use ScheduleWakeup(stop=true);
fixed scheduled jobs use CronDelete with their ID. A change to next_action alone
does not stop scheduling. On resume, reconcile schedules before creating another.
If these tools are unavailable, use one bounded invocation and report the limit.

Do not mark cycle or its nested workers explicit-only: that would block scheduled
skill invocation in supported Claude Code versions. Scale remains discoverable,
but the actual launch requires the shared plan-bound authorization check.
Optional PreToolUse hooks may call shared preflight checks; they supplement the
launcher contract and do not replace it or protect arbitrary shell side effects.

## Codex

Start with `codex --add-dir /path/to/project-infra-worktree`. `AGENTS.md` routes to
the same operating guide. Invoke `$sl-design`, `$sl-smoke`, `$sl-review`,
`$sl-repair`, `$sl-cycle`, `$sl-scale`, `$sl-survey`, or `$sl-status`.

Use an available independent agent context for reviewer/refuter roles with the
same inputs and read-only intent. When building a scripted coordinator, Codex
supports `codex exec --sandbox read-only --json` for event capture and
`--output-schema <schema-file>` for structured final output. Keep provider event
streams separate from synthloop's finalized review_result.json; map and validate
the result before recording it. Explicitly bind any resumed session ID to the
project/batch/role; do not use a global `--last` in parallel projects.

When independent execution is unavailable, report that missing review evidence
and stop before a pass checkpoint; a self-review is not an independent refutation.
Persist the shared cursor between invocations. A shell runner or task scheduler
can re-invoke a bounded cycle, but must stop on persisted terminal state and
reconcile jobs before retries. No Claude-only `/loop` command is required.

## Compatibility checks

After changing either adapter, run offline tests and the skill frontmatter
validator. Before claiming live platform compatibility, also run a small private
fixture through each actual CLI: interrupt after submission and after one review
chunk; resume; verify no duplicate job/chunk, identical shared metrics, and no
scale launch without a matching approval. These live checks consume model calls
and are separate from the repository's standard-library test suite.

Official references: [Claude skills](https://code.claude.com/docs/en/skills),
[subagents](https://code.claude.com/docs/en/sub-agents),
[scheduling](https://code.claude.com/docs/en/scheduled-tasks),
[hooks](https://code.claude.com/docs/en/hooks),
[Codex skills](https://developers.openai.com/codex/skills),
[CLI](https://developers.openai.com/codex/cli/reference), and
[non-interactive mode](https://developers.openai.com/codex/noninteractive).
