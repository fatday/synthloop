# CLAUDE.md

You are operating a data-generator development loop. This repo is the playbook;
the actual generator code lives in the user's own codebase. Your job is to run
the process, keep the records, and never skip a gate.

This is a PORTFOLIO repo: multiple generators are built with the same
technique at the same time, each in its own `data_projects/<name>/` folder.
Use `/status` for the portfolio view; scope a working session to one
generator unless explicitly doing a portfolio pass.

## How to work here

1. **Everything happens inside a project folder.** `data_projects/<name>/` holds the
   design spec, progress ledger, memory, and review history for one generator.
   No project folder, no work: create one from `templates/` first. Lessons
   that generalize get promoted to `playbook/` so every other in-flight
   generator inherits them.
2. **Read before acting.** On any task, read `data_projects/ENVIRONMENT.md`
   (shared infra, generator catalog, benchmark targets - instantiate it from
   `templates/environment.md` if missing), then the project's `progress.md`
   (current stage, next action, open questions) and `project_memory.md`
   (decisions and lessons) before doing anything else.
3. **Stages are entered through skills.** `/design`, `/smoke`, `/review`,
   `/repair`, `/scale` each load their stage's checklist from `playbook/`.
   Follow the checklist; the exit criteria are not optional.
4. **Write back before ending.** Every working session ends by updating
   `progress.md` (what happened, current stage, the single next action) and,
   if a decision or lesson was made, `project_memory.md`. If `data_projects/`
   is its own git repo, commit your state updates there (`git -C
   data_projects ...`).
5. **Public/private boundary.** `data_projects/` is workspace state and is
   gitignored by this (public) framework repo. NEVER commit anything under
   `data_projects/` to the synthloop repo, and never copy
   workspace-specific details (infra paths, internal names, quotas) into
   `playbook/` or `templates/` - generalize first.
6. **Human gates are hard gates.** Design approval and the scale-up go/no-go
   require an explicit human yes. Present the open questions and stop.

## Non-negotiable rules (from playbook/principles.md)

- Read stratified raw rows every QA cycle. Metrics passing is not evidence.
- Diagnose before patching. Auto-repair touches prompts, thresholds, and
  keyword lists only; code fixes require a written root cause and a new test.
- Every confirmed incident becomes a deterministic check or test (the ratchet).
- Commit the generator code before every launch, smoke or scale (provenance).
- Every designed behavior gets a usage counter from its first run. A
  capability with zero observed usage is a bug, not a maybe.
- Review findings get an adversarial refutation pass before they are reported.
  Evidence is full and verbatim, never truncated.
- Never write false claims about tool or environment behavior into prompts.
- When you fix a process failure, update the playbook in the same change.

## What you do NOT do

- Push, publish, or release anything without an explicit human request.
- Delete or regenerate existing data on your own initiative.
- Mark a stage complete when its exit criteria are unmet, however close.
