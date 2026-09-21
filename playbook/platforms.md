# Platform adapters

The shared playbook defines verdicts and authorization. These adapters provide
entry points, independent review and scheduling; neither owns a separate policy.
Record the CLI version used in the project runbook. Capability-detect unsupported
features and use the documented fallback rather than silently skipping a check.

Review defaults to the host's native agents. A user can select a custom API while
keeping Codex or Claude Code as the reviewer harness: follow
[review backends](review_backends.md) and the optional selection in
`data_projects/ENVIRONMENT.md`. This selection applies to review/refutation,
not to the coordinator's provider.

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
but the agent must verify that the actual launch is covered by the recorded
human authorization, following the shared scale workflow.

## Codex

Start with `codex --add-dir /path/to/project-infra-worktree`. `AGENTS.md` routes to
the same operating guide. Invoke `$sl-design`, `$sl-smoke`, `$sl-review`,
`$sl-repair`, `$sl-cycle`, `$sl-scale`, `$sl-survey`, or `$sl-status`.

Use an available independent agent context for reviewer/refuter roles with the
same inputs and read-only intent. Supply full rows and the pinned rubric, then
save findings in the project's review report. Bind resumed sessions to the right
project/batch/role; avoid resuming an unrelated session in parallel work.

When independent execution is unavailable, report that missing review evidence
and stop before a pass checkpoint; a self-review is not an independent refutation.
Persist the shared cursor between invocations. A shell runner or task scheduler
can re-invoke a bounded cycle, but must stop on persisted terminal state and
reconcile jobs before retries. No Claude-only `/loop` command is required.

## Improving the adapters

Use an actual small generator workflow to assess an adapter change: inspect
whether the agent follows the intended stage, catches real defects, resumes
unfinished work and avoids duplicate launches. Record observed failures and
adjust the relevant instructions. Do not claim live compatibility from reading
instructions alone.

Official references: [Claude skills](https://code.claude.com/docs/en/skills),
[subagents](https://code.claude.com/docs/en/sub-agents),
[scheduling](https://code.claude.com/docs/en/scheduled-tasks),
[Codex skills](https://developers.openai.com/codex/skills),
[CLI](https://developers.openai.com/codex/cli/reference), and
[non-interactive mode](https://developers.openai.com/codex/noninteractive).
