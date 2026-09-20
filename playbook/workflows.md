# Shared command workflows

Both `.claude/skills/` and `.agents/skills/` route here. Workflow policy lives
in the stage files and runtime contract, not in platform-specific copies.
For generator work, read CLAUDE.md, principles.md, ENVIRONMENT.md, state.json,
progress.md and project_memory.md as applicable. Framework maintenance needs
no project bootstrap. Honor existing authorization for the same concrete action.

## survey

Follow `survey.md`. Limit inspection to user-designated workspace roots, not
every readable directory on the machine. Create data_projects/ and its README
from templates if needed, then instantiate ENVIRONMENT.md. Inspect directory
roles by evidence, preserve confirmed entries, and ask only about unknown or
ambiguous roles. A data-infra root is required before implementation.

## design

Create the project from design_spec.md, progress.md, project_memory.md,
state.json, baseline.json, and review_instruction.md (as review_instructions/v1.md).
Bootstrap survey if necessary. Follow `00_context.md` and `01_design.md`; use
infra evidence before asking questions. Fill baseline values as proposals,
including budgets and minimum sample sizes. Present the concrete design and
remaining questions before the human gate. Record approval against the baseline
hash per `runtime.md`. Existing approved designs resume at the recorded stage.
After approval, follow `02_implement.md` in the infra worktree. Do not skip the
implementation stage merely because it has no dedicated slash command.

## smoke

Requires stage 2 complete with a runnable runbook and design approval. Follow
`03_quality_loop.md` 3.1 and `runtime.md`. First run resume and reconcile any
existing job. Respect the pinned functional/validation batch plan and budgets;
reserve the batch identity before launch, commit code and capture provenance.
Run Track A over all emitted rows and a stratified raw-row read. Persist output
handles, inventory, manifest and the next review action. A tiny functional smoke
does not establish a validation pass or a statistical coverage failure.

## review

Follow `03_quality_loop.md` 3.2-3.3 and `review_rubric.md`. Review the specified
batch, never silently substitute another. Validate its manifest, inventory and
pinned rubric. Resume incomplete review chunks. Use independent reviewer and
refuter contexts per `platforms.md`, retaining full evidence. Report A, B and
joint rates with denominators and cohort sample sizes. Sampled B is explicitly
incomplete for the validation gate. Write review_result.json and one human
summary; use check-batch, then record-review once final. Do not relax the rubric
or count a batch twice. Update progress.md from state.

## repair

Follow `03_quality_loop.md` 3.4-3.5. Diagnose a confirmed finding before edits.
Apply the smallest generator fix or acceptance loosening within the approved
surface. Code fixes need a new fail-on-parent/pass-on-fix test and the suite.
Compare acceptance on the SAME retained rows; inspect newly accepted and newly
rejected examples under the pinned rubric. Independent verification challenges
the fix as well as the finding. Net-tightening, judge/ratchet weakening, frozen
baseline changes and scope expansion are proposals, not autonomous edits.
Retain old data for audit/replay, commit the fix, append design deltas and
memory, and validate a fresh batch. Candidate review rules do not become the
evaluation rubric automatically.

## cycle

Drive smoke → review → repair using the procedures above and stage 3 in full.
Follow state.json at every transition. A single invocation may continue through
multiple cycles within the approved budget; platform scheduling is optional.
No worker should keep a scheduler waiting just to obtain another iteration.
The baseline target is authoritative. If the request includes a different target,
prepare a new checkpoint with that target and retain the previous evidence.
Record the user's explicit authorization when it establishes the new scope;
never silently ignore the requested target or overwrite the frozen baseline.

On first clean pass, run a fresh-seed confirmation at the same fingerprint.
On two consecutive clean passes, stop and present the checkpoint and concrete
scale plan. Stop earlier on hard gates, confirmed regression/oscillation,
unreconciled infra failure, or budget exhaustion. Persist stop reason, HEAD,
rollback anchor, autonomous commits and coverage deltas. Cancel actual scheduled
wakeups on terminal stops. Never auto-scale; see `runtime.md` and `platforms.md`.

## scale

Follow `04_scale.md` and `runtime.md`. First complete the launch plan and
preflight, then verify existing explicit authorization against its hash. Request
approval only if missing/stale; a new session alone does not invalidate it.
Two clean passes, ratified deltas and matching provenance are required. Run
check-gates immediately before launch, then submit the exact approved plan with
an idempotency key. Monitor with the approved live budgets/failure policy.
Final at-scale QA and raw-row reading are required. Publication is separately
authorized. Write the postmortem, state and progress summary.

## status

Read-only: read shared environment if present, and each requested project's
state/progress/memory/latest review. Do not initialize missing state as a side
effect. Show generator, stage/cursor, next action, active job, last verdict,
blocked-on and open questions. Flag missing/invalid state and stale projects;
do not repair them during status. Use resume for reconciliation advice only.
