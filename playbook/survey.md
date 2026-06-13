# Workspace survey

**Purpose**: classify every directory the agent can reach, so later stages
know which repo is the generation infra, which is a benchmark, which is seed
data. Run once when a workspace is set up, and again whenever directories are
added. Feeds the "Workspace directories" table in `data_projects/ENVIRONMENT.md`.

(The `/survey` skill is a Claude Code shortcut to this procedure; any agent can
run it by following the steps below.)

## Procedure

1. Enumerate accessible roots: the current workspace plus every additional
   directory the session can reach.
2. For each root, classify by INSPECTION (read the README, the project config -
   pyproject/package.json/Makefile - and the top-level structure; do NOT guess
   from the directory name). Roles:
   - **data-infra**: a generation framework - a generate CLI or entry point,
     generator base classes or a registry, prompt templates, output
     serialization. This is where generator code gets written.
   - **benchmark**: an evaluation harness - scoring/grading code, ground-truth
     or test-case files, eval runners, metrics. Read-only reference; its
     SCORING CODE (not its README) defines format conventions for targeted data.
   - **seed-corpus**: mostly data files (jsonl/parquet/csv/...) with little
     code. Input material for generators.
   - **vendored-reference**: a third-party project mirrored locally (upstream
     license, no local project config). Read-only; note what it is canon for.
   - **serving/infra**: model serving, cluster tooling, deployment.
   - **unknown**: cannot tell from inspection.
   Classification is by evidence: a directory named "benchmark" that contains a
   generation CLI is data-infra.
3. Record each row (path, role, the evidence that decided it, what it is used
   for) in the `data_projects/ENVIRONMENT.md` directories table. Preserve
   human-confirmed rows; propose changes to them with a note.
4. Present the table; flag `unknown` and low-confidence rows for the human to
   confirm.

## The one hard requirement

Exactly one role is REQUIRED: **data-infra**. Every other role is optional
context. If NO accessible directory classifies as data-infra, STOP: the
workspace cannot build generators until the data-generation codebase is made
an accessible directory (in Claude Code, `claude --add-dir <path>` or the
in-session `/add-dir <path>`; with another tool, however it grants directory
access), or until the human points out which existing directory it is. Do not
let design proceed past the design stage without a confirmed data-infra root.
