---
name: survey
description: Detect and classify every accessible workspace directory (data infra, benchmark, seed corpus, ...) and record the roles in ENVIRONMENT.md. Run on first setup and whenever directories are added. Usage - /survey
---

# /survey

Classify what each accessible directory IS, so every later skill knows which
repo to use for what. Runs automatically as part of `/design`'s environment
bootstrap; run it manually after `/add-dir` or when the workspace changes.

1. Enumerate accessible roots: the current workspace plus every additional
   directory the session can reach.
2. For each root, inspect (do not guess from the name alone): the README,
   project config (pyproject/package.json/Makefile), and the top-level
   structure. Classify into one of:
   - **data-infra**: generation framework - has a generate CLI or entry
     point, generator base classes or a registry, prompt templates, output
     serialization. This is where generator code will be written.
   - **benchmark**: evaluation harness - scoring/grading code, ground-truth
     or test-case files, eval runners, metrics. This is read-only reference;
     its SCORING CODE defines format conventions for targeted data.
   - **seed-corpus**: mostly data files (jsonl/parquet/csv/zst) with little
     code. Input material for generators.
   - **vendored-reference**: a third-party project mirrored locally (upstream
     license, no local project config). Read-only; note what it is canon for.
   - **serving/infra**: model serving, cluster tooling, deployment.
   - **unknown**: cannot tell from inspection.
3. Record evidence per classification (one line: the files that decided it).
4. Write or update the "Workspace directories" table in
   `data_projects/ENVIRONMENT.md`. Preserve rows the human already confirmed;
   only propose changes to them with a note.
5. Present the table to the human, flagging `unknown` rows and any
   low-confidence calls for confirmation. Record confirmations in the table.

Rules:
- **Exactly one role is REQUIRED: data-infra.** Every other role (benchmark,
  seed-corpus, vendored-reference, serving/infra) is optional context. If NO
  accessible directory classifies as data-infra, STOP and tell the user:
  the workspace cannot build generators until they add their data-generation
  codebase (`/add-dir <path>` or `claude --add-dir`), or point out which
  existing directory it is if the classification missed it. Do not let
  `/design` proceed past the design stage without a confirmed data-infra
  root.
- Classification is by INSPECTION, with evidence. A directory named
  "benchmark" that contains a generation CLI is data-infra.
- A workspace may have several directories of the same role (two infra
  repos); the table's "used for" column disambiguates which projects use
  which.
- Read-only: this skill modifies only ENVIRONMENT.md.
