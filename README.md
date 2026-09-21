# synthloop

**English** | [简体中文](README.zh-CN.md)

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/b84fdbea-c99a-419a-ac46-51603c1507c7" />

**An agentic playbook for building, reviewing, and iterating LLM data generators.**

synthloop is not a data generation library. It is the *process* around one: a
stage-by-stage playbook and fill-in templates that let a coding agent (with a
human in the loop) take a synthetic-data generator from idea to large-scale
release, with explicit quality checks, durable state and auditable human gates.

The playbook is **agent-agnostic** - any coding agent or a human can run it by
reading `playbook/` - with **first-class Claude Code support** via the slash
skills in `.claude/skills/` and **first-class Codex support** via repo skills
in `.agents/skills/`. Pick a track:
[Claude Code](#path-a-claude-code),
[Codex](#path-b-codex), or
[any other agent](#path-c-any-other-agent).

```
Learn -> Design -> Implement -> [ Small-scale generate -> Automated QA -> Repair ]* -> Scale & Release
                                          ^ the loop you live in ^
```

## Why

Synthetic data efforts fail in repeatable ways: metrics pass while the data is
wrong, auto-repair loops patch symptoms until the distribution quietly narrows,
capabilities ship dark and nobody notices, and six weeks later nobody can say
which code produced which rows. Each failure has a known countermeasure. This
repo encodes them as checklists an agent can follow and a human can audit.

The core bets:

1. **Dual-track QA**: agent review and deterministic rule checks catch disjoint
   failure classes. You need both, every cycle.
2. **Reading raw rows is the highest-yield QA activity.** Judges and rules
   inherit each other's blind spots; human (and agent) eyes on stratified raw
   samples catch what nothing else does.
3. **Diagnose, then patch.** Autonomous repair can fix prompts, code and
   constants within the approved surface, without tightening acceptance.
   Code fixes need a written diagnosis and a test that fails before the fix.
4. **The ratchet**: every incident becomes a permanent deterministic check.
   Quality cannot regress silently.
5. **Provenance and telemetry are part of generation, not an afterthought.**
   Commit before every launch; count every designed behavior from minute one.

## Repository map

```
CLAUDE.md                  Canonical operating guide (agent-neutral; auto-loaded
                           by Claude Code)
AGENTS.md                  Entry point for any other agent; routes to CLAUDE.md
                           and the playbook
playbook/
  survey.md                Classify workspace directories (run once / on change)
  00_context.md            Stage 0: learn the domain and the target
  01_design.md             Stage 1: design spec, coverage spec, reality checks
  02_implement.md          Stage 2: generator + offline replay + telemetry hooks
  03_quality_loop.md       Stage 3: the small-scale generate/QA/repair loop
  04_scale.md              Stage 4: scale-up, monitoring, release, postmortem
  principles.md            The distilled rules. Read this first.
  review_rubric.md          How data review is conducted and reported
  review_backends.md        Optional review APIs using native agent harnesses
  workflows.md             Shared command workflows for both platforms
  recovery.md              Session recovery, records and parallel coordination
  platforms.md             Claude Code and Codex execution adapters
templates/
  environment.md           Workspace-wide context: infra, generator catalog,
                           benchmark targets. Instantiated once per workspace as
                           data_projects/ENVIRONMENT.md (note the case change:
                           lowercase template -> uppercase instance)
  design_spec.md           Per-generator design spec (with mandatory questions)
  review_instruction.md    Versioned review instructions for QA agents
  progress.md              Human-readable progress ledger
  project_memory.md        Per-generator durable memory (decisions, lessons)
  data_projects_README.md  Seed README copied in when data_projects/ is created
.claude/agents/            Independent reviewer and refuter definitions
.claude/skills/            Slash-skills: /survey /design /smoke /review /repair
                           /cycle /scale /status
.agents/skills/            Codex repo skills: $sl-survey $sl-design
                           $sl-smoke $sl-review $sl-repair
                           $sl-cycle $sl-scale $sl-status
data_projects/             YOUR workspace state (gitignored here; often its
                           own private repo): one folder per generator
LICENSE                    MIT
```

## Setup (both paths)

synthloop sits NEXT TO your data-generation codebase; it never contains
generator code. Clone them side by side:

```
~/work/
  my-data-infra/    # your codebase: generator code, engines, CLI, tests
  synthloop/        # this repo: playbook, skills, per-generator state
```

The agent's brain is in synthloop (the playbook + skills); its hands are in
your infra repo (code, tests, generated data). The division of labor never
changes: **generator code, tests and data live in your repo; specs, ledgers,
memory and review history live here.** The agent runs the playbook using your
existing infra. Your code PRs stay clean of process artifacts, and the progress
ledger lets another session continue the work.

Then pick a path: **Path A (Claude Code)** for the first-class slash-skill
flow, **Path B (Codex)** for repo-scoped skills, or **Path C (any other
agent)** to drive the same loop by reading the playbook.

## Path A: Claude Code

Launch Claude Code from synthloop, granting access to your infra repo:

```bash
cd ~/work/synthloop
claude --add-dir ~/work/my-data-infra
```

`--add-dir` is repeatable for workspaces with several relevant repos
(a vendored benchmark, a seed-data directory, a second infra repo):

```bash
claude --add-dir ~/work/my-data-infra --add-dir ~/work/some-benchmark
```

To avoid retyping, persist your paths in
`synthloop/.claude/settings.local.json` (personal, not committed - each
teammate points at their own clones), then launching is just `claude`:

```json
{
  "permissions": {
    "additionalDirectories": ["~/work/my-data-infra", "~/work/some-benchmark"]
  }
}
```

You can also add a directory to a live session with `/add-dir <path>`.

You do not need to tell the agent what each directory is: `/survey` inspects
the supplied workspace roots and classifies them (data-infra, benchmark, seed-corpus,
vendored-reference, ...) with evidence, records the table in
`data_projects/ENVIRONMENT.md`, and asks you to confirm only the ambiguous
ones. It runs automatically during `/design`'s first-time bootstrap; re-run
it whenever you add directories.

Only one role is mandatory: a **data-infra** directory (your generation
codebase). Without one the agent will stop and ask for it before any
implementation work; benchmarks, seed corpora, and the rest are optional
context that sharpen the design when present.

### First session

Type `/design <your-first-generator>`. The skill notices
`data_projects/ENVIRONMENT.md` is missing and builds it first - partly by
interviewing you, mostly by reading your infra repo (the CLI, the generator
patterns, existing generators to catalog, benchmark targets). Every future
project and session inherits that knowledge for free.

### The loop, per generator

```
/design my-generator     # interview + spec with coverage numbers -> YOUR approval (gate 1)
                         # agent implements in your infra repo, per the spec
/smoke my-generator      # commit, small batch, coverage tally, raw-row read
/review my-generator     # dual-track QA + refutation pass -> verdict
/repair my-generator     # diagnose-then-patch, ratchet tests
                         # loop smoke -> review -> repair until 2 clean passes
                         # -> YOUR approval (gate 2)
/scale my-generator      # preflight, launch, monitoring, release
/status                  # portfolio dashboard across all generators
```

You show up at the two gates, the open-question queues, and whenever you feel
like reading rows (keep doing that - it is the highest-yield QA there is).

### Running the inner loop hands-off

`/cycle` drives the bounded smoke → review → repair loop using the same
workflow as Codex. Optional `/loop` scheduling can re-invoke it:

```
/cycle my-generator          # drive to two clean passes or a hard stop
/loop /cycle my-generator    # optional scheduling; terminal stops cancel wakeups
```

The approved baseline sets the joint pass-rate target (proposed default 95%),
minimum cohort sample sizes, coverage floors, drift and cycle/cost/time budgets.
Track A checks ALL emitted rows, including rejects; Track B uses the pinned
rubric. Two separate 95% rates do not imply 95% joint acceptance. A sampled
semantic review cannot silently count unreviewed rows as good.

A tiny functional smoke checks directed paths, not population frequencies.
Validation uses the approved sample sizes. Ordinary random coverage fluctuation
is not automatically a regression; evaluate frozen floors, drift and paired replay.

The first clean pass triggers a new-seed confirmation batch on the same validated
version. Two consecutive clean passes stop for human review of the exact scale
plan. Any edited/failed cycle breaks the streak. Hard gates, confirmed regression,
unreconciled infrastructure failures and budget limits stop earlier. Net-tightening
acceptance, weakening judges/ratchets, changing frozen baselines and expanding
scope remain human-gated. The loop never auto-scales.

### Day to day

- **Resume anything**: new session -> `/status` -> pick a project -> the agent
  reads progress.md and checks referenced jobs and outputs. Active jobs are
  reconciled and incomplete reviews resume from their saved chunks.
- **Several generators at once**: one session, infra worktree and output prefix
  per generator, with a single writer per project. Serialize shared environment
  and playbook updates; project folders alone do not isolate a shared infra HEAD.
  Record the framework version alongside batch metadata.
- **Teammates**: clone both repos, run the same two commands, inherit
  everything - the environment file, the playbook, and each project's state.

## Path B: Codex

Launch Codex from synthloop, and make your data-infra repo accessible in the
same workspace/session:

```bash
cd ~/work/synthloop
codex --add-dir ~/work/my-data-infra
```

Codex reads `AGENTS.md` automatically and discovers repo skills from
`.agents/skills/`. Invoke synthloop workflows with `/skills` or by mentioning
the skill name:

```
$sl-design my-generator
$sl-smoke my-generator
$sl-review my-generator
$sl-repair my-generator
$sl-cycle my-generator
$sl-status
```

The `sl-*` prefix is intentional: Codex has built-in slash commands such as
`/status` and `/review`, and those are Codex session commands, not synthloop
workflow commands.

### First session

Start with `$sl-design <your-first-generator>`. If
`data_projects/ENVIRONMENT.md` is missing, the skill routes through
`$sl-survey` first, classifies the accessible roots, and instantiates the
shared environment file.

### The loop, per generator

```
$sl-design my-generator     # spec + coverage numbers -> YOUR approval
$sl-smoke my-generator      # commit, small batch, coverage tally, raw-row read
$sl-review my-generator     # dual-track QA + refutation pass -> verdict
$sl-repair my-generator     # diagnose-then-patch, ratchet tests
$sl-cycle my-generator      # smoke -> review -> repair loop to checkpoint
$sl-scale my-generator      # only after explicit scale-up approval
$sl-status                  # portfolio dashboard
```

Everything else is the same contract as Claude Code: `CLAUDE.md` is canonical,
`playbook/` is the source of truth, human gates are hard gates, and every
session updates progress.md. See
[platform adapters](playbook/platforms.md) for independent review and automation.

## Path C: any other agent

Same Setup as above (clone side by side). The Claude Code skills are ergonomic
sugar, and the Codex skills are the same kind of shortcut. The substance is
`playbook/` (stages + principles + rubric) and `templates/`, plain markdown any
coding agent or human can follow.

To run synthloop with another tool (Cursor, Gemini CLI, Aider, a custom
harness):

1. Point your agent at the repo. Tools that read `AGENTS.md` pick up the entry
   guide automatically; otherwise tell your agent to read `AGENTS.md` first.
2. `AGENTS.md` routes to `CLAUDE.md` (the canonical, agent-neutral operating
   rules) and to the `playbook/` stages, with a table mapping each slash skill
   to "what to do without it" (including the workspace `survey` and `status`
   steps that have no numbered stage file).
3. First time, follow the four-step bootstrap in `AGENTS.md`'s "First time"
   section (create `data_projects/`, copy `templates/data_projects_README.md`
   into it, run `playbook/survey.md`, instantiate `data_projects/ENVIRONMENT.md`
   from `templates/environment.md`). Then drive the loop by reading the stage
   file for each step (`playbook/00_context.md`, `01_design.md`,
   `03_quality_loop.md`, `04_scale.md`) and following its checklist and exit
   criteria - the same two human gates apply.

The core stage rules and templates are platform-neutral. Both skill sets route
to [shared workflows](playbook/workflows.md); platform-specific execution details
live separately in [platforms.md](playbook/platforms.md).

Reviewers can optionally use a user-provided model API while retaining the
Codex or Claude Code harness. Record the selection in your workspace's
`ENVIRONMENT.md`; see [review backends](playbook/review_backends.md) for setup,
protocol requirements, and the distinction between native subagents and CLI
worker sessions. With no explicit selection, independent review agents use the
current session's model, provider and authentication; no extra API setup is
requested. An incomplete or failed explicitly selected API is reported rather
than silently replaced with the session model.

## Public framework, private state

This repo is the FRAMEWORK only. Everything workspace-specific - your
instantiated `ENVIRONMENT.md`, your project folders, your operational
scripts - lives under `data_projects/`, which is **gitignored here by
design**. Ordinary `git add .` excludes that directory; keep private details
out of tracked templates/playbook files too. Gitignore is not a privacy boundary
against force-adds or copying internal content into public files.

(That is also why you will not see a `data_projects/` folder on the hosted
repo: it does not exist until first use. `/design` creates it locally, and
it stays local or in your private repo, never here.)

Two ways to run your workspace state:

```bash
# 1. Local-only (solo): just use it; it stays untracked.
/design my-generator          # creates data_projects/ on first use

# 2. Private repo (teams, recommended): version the state separately.
cd ~/work/synthloop
git clone git@your-host:your-org/synthloop-projects.git data_projects
```

With option 2, agents commit process state (progress ledgers, specs, memory)
to the private repo as they work, teammates clone the same pair of repos,
and the public framework stays clean.

## Continuing work

The agent follows the playbook directly using the existing infra's commands and
records. Keep ongoing jobs, review progress, batch results and the next action
in progress.md. [Recovery guidance](playbook/recovery.md) explains how to resume
without duplicating work and how to reuse matching authorization across sessions.
No framework runtime, required JSON state files or framework test suite is needed.

## The human's job

You are the final gate and the direction-setter. The loop protects your
attention for the two things only you can do: judging whether the data is
*actually what you want* (taste), and verifying claims against sources the
agent does not control (your dashboards, your spot reads). Everything else is
delegated.

## License

MIT. See LICENSE.
