# CLAUDE.md

You are operating a data-generator development loop. This repo is the playbook;
the actual generator code lives in the user's own codebase. Your job is to run
the process, keep the records, and never skip a gate.

> This file is the canonical operating guide for ANY agent working in this
> repo, not only Claude Code (which just auto-loads it). Non-Claude agents are
> routed here by `AGENTS.md`. The OPERATING rules (how to work, the gates, what
> not to do) live only here; the data-quality principles they reference are
> stated canonically in `playbook/principles.md` and only summarized below.

This is a PORTFOLIO repo: multiple generators are built with the same
technique at the same time, each in its own `data_projects/<name>/` folder.
Use `/status` for the portfolio view; scope a working session to one
generator unless explicitly doing a portfolio pass.

## How to work here

1. **Generator work happens inside a project folder.** `data_projects/<name>/`
   holds the design spec, progress ledger, memory, and review history for one
   generator; create it from `templates/` before generator work starts.
   Lessons that generalize get promoted to `playbook/` so every other
   in-flight generator inherits them. (Questions, discussion, and edits to
   the playbook itself need no project folder - apply this process to
   building generators, not to every interaction.)
2. **Read before acting.** On any task, read `data_projects/ENVIRONMENT.md`
   (shared infra, generator catalog, benchmark targets - instantiate it from
   `templates/environment.md` if missing), then the project's `progress.md`
   (current stage, next action, open questions) and `project_memory.md`
   (decisions and lessons) before doing anything else.
3. **Stages are entered through skills (Claude Code) or by reading the
   playbook directly (any agent).** `/design`, `/smoke`, `/review`, `/repair`,
   `/scale` are thin routers that load their stage's checklist from
   `playbook/`; without them, open the matching `playbook/` file yourself
   (see `AGENTS.md` for the mapping). Either way, follow the checklist; the
   exit criteria are not optional.
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
6. **Human gates are hard gates.** Initial design approval, **major design
   pivots**, and the scale-up go/no-go require an explicit human yes. The
   autonomous quality loop (`/cycle`, `/loop /cycle`) runs the inner loop on its
   own but **stops and hands back at the target checkpoint** for human review
   and steering, and **proposes-but-never-applies** anything that net-tightens
   acceptance, relaxes the judge, weakens a ratchet, expands scope, or moves the
   frozen baseline. Present the open questions and stop.
7. **Context management — compaction-safe by construction.** A long autonomous
   run WILL be compacted: the harness auto-summarizes when context grows, and an
   agent can neither measure the exact threshold nor trigger `/compact` itself
   (both are harness-controlled). So do NOT try to detect "90% full" — instead
   keep `progress.md` a COMPLETE, self-contained resume point at ALL times (stage
   cursor + the single next action + the job/commit/file refs needed to
   continue), updated at every sub-stage transition, never batched to the end.
   Then compaction (auto or human-invoked) is LOSSLESS: after any compaction or
   session reset, re-read the cursor and the relevant `project_memory.md` entries
   and continue exactly where you were. When the run has grown long (heuristically
   ~80% of the window — you can't read the exact %) AND you are at a safe pause
   ("free" — between cycles or waiting on a job, NOT mid-edit/mid-launch),
   proactively write a fresh full checkpoint and tell the human it is safe to
   `/compact`. (You cannot trigger `/compact` yourself; the human runs it or the
   harness auto-compacts — the complete checkpoint makes either lossless.)
8. **State budgets — the resume point must stay readable.** `progress.md`
   holds the current state (stage, next action, cursor, blockers, open
   questions), the pinned sections (smoke spec, runbook, gates), the last ~10
   entries of each ledger and the last ~5 cursor entries. At each stage exit, or
   when it passes ~25 KB, move older entries and finished-investigation notes
   VERBATIM to `progress_ledger.md` (append-only, newest first). Budgets are in
   bytes and characters, not lines: an unwrapped line can hold a page. A cursor
   entry is at most ~1,000 characters: what happened, the numbers that matter,
   refs, the single next action; details live in the review and build files it
   links. `project_memory.md` holds decisions in force and lessons; when it
   passes ~25 KB, consolidate it (merge duplicate lessons, list superseded
   decisions in one line each, keep the full text in
   `project_memory_archive.md`) and promote lessons that generalize to
   `playbook/`. The playbook follows the same rule: a new lesson merges into or
   replaces an existing bullet before a new bullet is added.
9. **Workspace hygiene.** Temp output, worktrees and data copies follow
   `playbook/workspace_hygiene.md`: job-scoped scratch, worktrees listed in
   `progress.md` and removed when their round closes, an audit at every stage
   exit. Deleting anything still needs the human's approval (see below).

## Non-negotiable rules (summary of playbook/principles.md - that file is canonical)

- Read stratified raw rows every QA cycle. Metrics passing is not evidence.
- **Reach the bar by raising RAW generation quality, never by shedding.** The
  target is cleared only when the generator is good enough that the *whole accepted
  batch* passes both tracks ≥ target — NOT by adding reject gates/filters or
  dropping hard rows to inflate the pass-rate (a narrower dataset that scores high
  is strictly worse than an honest lower score on the full distribution). The fix
  for a low pass-rate is "make the generator produce better rows," not "stop
  accepting the bad ones."
- Diagnose before patching, and **repair monotonically**: autonomous repair may
  fix the generator or LOOSEN acceptance (code included, with a root cause + a
  test that fails-on-parent/passes-on-fix), but NEVER net-tightens it. Any
  net-tightening of acceptance, judge relaxation, ratchet weakening, scope
  expansion, or major pivot is propose-and-stop (human-gated).
- Pass is QUALITY, not yield, and is a **TWO-TRACK AND**: a batch passes only when
  **BOTH (a) the Track-B reviewer (LLM) pass-rate on accepted rows ≥ target AND
  (b) the Track-A deterministic-check pass-rate ≥ target** — each track measured
  and thresholded INDEPENDENTLY (do NOT merge them into one "combined" number; both
  must clear the bar on their own). Track-B is scored on the human-owned **pinned
  rubric**; Track-A is the deterministic sweep (no false-denial/fabrication/leak/
  structural fail). Both use the worst-cohort rule. This is NOT accept-rate/yield
  (the gates legitimately reject imperfect attempts, so yield runs below target;
  chasing yield only loosens real gates). The deterministic track is a conservative
  FLOOR that can read high while the LLM track is still failing — which is exactly
  why both are required, not either-or or a blend. It is yoked to a **frozen
  coverage floor** the loop cannot move (so quality can't be gamed by shedding hard
  rows), and a cycle that applied any edit cannot pass (validate on a fresh
  same-commit batch first).
- Every pass rate is reported with its n and 95% interval, and a change between
  batches counts only when it exceeds the noise band (sampling interval and
  reviewer spread). After two consecutive rounds of one lever class move
  nothing beyond noise, stop that class and present structural options.
- The reviewer rubric and the ratchet/eval harness are human-owned and
  **append-only** for the loop — add or tighten, never relax or weaken.
- Every confirmed incident becomes a deterministic check or test (the ratchet).
- Commit the generator code before every launch, smoke or scale (provenance).
- Every designed behavior gets a usage counter from its first run. A
  capability with zero observed usage is a bug, not a maybe.
- Review findings get an adversarial refutation pass before they are reported.
  Evidence is full and verbatim, never truncated.
- Never write false claims about tool or environment behavior into prompts.
- When you fix a process failure, update the playbook in the same change.

## What you do NOT do

- Push, publish, or release anything (including `/scale`) without an explicit
  human request.
- Net-tighten acceptance, relax the reviewer rubric, weaken/skip/delete a
  ratchet test, or adopt a scope expansion / creative direction on your own
  initiative — propose with evidence and stop.
- Run the loop below the human-set target floor, or edit a frozen baseline
  section of the design spec (append a dated delta instead).
- Delete or regenerate existing data on your own initiative.
- Mark a stage complete when its exit criteria are unmet, however close.
