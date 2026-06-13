# AGENTS.md

Entry point for any coding agent (Codex, Cursor, Gemini CLI, Aider, a custom
harness, or a human). synthloop is an agent-operated playbook for building,
reviewing, and iterating LLM data generators; this file tells a non-Claude-Code
agent how to run it.

## The operating guide is `CLAUDE.md`

`CLAUDE.md` holds the operating rules - how to work in this repo, the
non-negotiables, the human gates, what not to do. It is named for Claude Code
(which auto-loads it), but its content is **agent-neutral**: read it as your
operating guide regardless of tool. There is no second copy of the rules to
drift from; `CLAUDE.md` is canonical.

## Stages live in `playbook/`

The work is a five-stage loop, preceded by a one-time workspace survey. Each
file is a self-contained checklist with exit criteria - runnable by reading it
and following it, no tooling required:

- `playbook/survey.md` - classify workspace directories (run once / on change)
- `playbook/00_context.md` - learn the domain and target
- `playbook/01_design.md` - design spec, coverage spec, reality checks
- `playbook/02_implement.md` - generator + offline replay + telemetry
- `playbook/03_quality_loop.md` - the generate / QA / repair loop
- `playbook/04_scale.md` - scale-up, monitoring, release, postmortem
- `playbook/principles.md` - the distilled rules (read first)
- `playbook/review_rubric.md` - how review is conducted and reported

Per-generator state lives under `data_projects/<name>/`, instantiated from
`templates/`. Read `data_projects/<name>/progress.md` to resume.

## Slash skills are an optional Claude Code convenience

`.claude/skills/` provides ergonomic entry points for Claude Code. Each skill
routes to the playbook; the "Without it, do this" column below is the
tool-neutral equivalent, including the few operational details a skill adds on
top of its stage file. If your tool does not support Claude Code skills, ignore
that folder and follow this table.

| Skill | Without it, do this |
| --- | --- |
| `/survey` | Run `playbook/survey.md`: classify each accessible directory (data-infra required, else STOP and ask for it; benchmark/seed-corpus/etc optional); record the table in `data_projects/ENVIRONMENT.md`. |
| `/design <name>` | Run `playbook/00_context.md` then `01_design.md`; create the project folder from `templates/`; stop at the human design gate. |
| `/smoke <name>` | Run the small-scale-generation steps in `playbook/03_quality_loop.md` 3.1 (commit first, generate, coverage tally, raw-row read). |
| `/review <name>` | Run the dual-track QA in `playbook/03_quality_loop.md` 3.2 + `review_rubric.md` (deterministic checks, agent review with refutation pass + kill-rate, raw-row read, verdict). |
| `/repair <name>` | Run the diagnose-then-patch steps in `playbook/03_quality_loop.md` 3.4 (diagnosis, scoped fix, ratchet test). |
| `/scale <name>` | Run `playbook/04_scale.md` (preflight, launch, monitor, release, postmortem). Requires the scale-up human gate. |
| `/status [name]` | Read `data_projects/*/progress.md` and print the portfolio table (generator, stage, next action, blocked-on, last-batch verdict); list projects with open questions for the human; flag staleness (a project whose next action has not changed across multiple sessions, or whose last entry is old relative to others). Read-only. |

## First time

Read `CLAUDE.md`, then `playbook/principles.md`. If `data_projects/` does not
exist yet, create it and copy `templates/data_projects_README.md` to
`data_projects/README.md` (the seed scaffold for the workspace). Then run
`playbook/survey.md` to classify your directories and instantiate
`data_projects/ENVIRONMENT.md` from `templates/environment.md` - this is the
shared context every generator inherits, and stage 0 expects it to exist.
With that in place, start your first generator at `playbook/00_context.md`.
