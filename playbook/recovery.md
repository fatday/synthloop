# Resume and coordination

Keep the project's current stage, next action and ongoing work in progress.md.
Use the existing infra's job handles, batch metadata and review reports; no
separate state format or framework runner is required.

## Resume an interrupted session

1. Read progress.md and project_memory.md, then inspect the referenced outputs
   and logs. Reconcile what actually happened before following the next action.
2. If a generation job was submitted, look it up by job or batch ID. Continue
   monitoring a running job; review completed output. If submission was interrupted,
   check the scheduler and output directory before retrying. An unknown result
   is a reason to investigate, not to submit a duplicate job.
3. For a partial review, read saved findings and resume only unfinished chunks.
   Record completed chunks as work proceeds, not only when the session ends.
4. Count each batch once. Two clean passes require fresh batches with distinct
   seeds and the same code, behavior config, model, evaluation rubric and design
   baseline. Changes to those inputs require fresh validation.
5. Preserve the stop reason and remaining budget. Resolve the cause before
   continuing; cancelling a platform loop requires cancelling its actual wakeup.

## Records that matter

Record batch ID, output location, code commit, config/prompt/model versions, seed,
evaluation rubric version and review result in the batch ledger or link to the
infra's existing metadata. Retain rejected rows as well as accepted rows.
Use versioned files or immutable snapshots when inputs are otherwise mutable;
do not introduce a second metadata system if the infra already tracks them.

Record human decisions with their source, date and approved scope. Existing
authorization remains valid across sessions for the same action. Before scale,
compare the actual code, inputs, command, volume and budget with the approved
plan. A changed plan needs the corresponding authorization; a new session alone
does not. Publishing remains a separate authorization.

## Parallel projects

Use a separate infra worktree and output location per generator. Keep one writer
per project and coordinate changes to shared ENVIRONMENT.md or playbook files.
Separate project folders do not isolate a shared infra HEAD or shared API quota.
Check live usage and remaining budget through the infra/provider as work proceeds.
