# data_projects/

> Copied here from synthloop's `templates/data_projects_README.md` when the
> workspace was created. This whole directory is YOUR workspace state: it is
> gitignored by the public synthloop repo and is typically its own PRIVATE
> git repo, so internal infra details never touch the open-source project.

The portfolio: one folder per generator, all sharing the same playbook.
Multiple generators are expected to be in flight at once, at different
stages, possibly worked by different sessions or people in parallel.

`ENVIRONMENT.md` (instantiated from `templates/environment.md`) lives at this
level: the workspace-wide context every project inherits - the data
generation infra and how to run it, the catalog of existing generators worth
copying from, the benchmark styles being targeted (with their format quirks),
and external resources/quotas. Agents read it before any project work, and
write back what they learn so the next generator starts smarter.

```
data_projects/<name>/
  design_spec.md             The contract (coverage numbers, reality checks)
  progress.md                Resume point: stage, next action, ledgers, gates
  project_memory.md          Decisions, diagnoses, lessons (newest first)
  review_instructions/
    v1.md, v2.md, ...        Versioned reviewer guidance; latest wins
  reviews/                   Batch review summaries (one file per batch)
  patches/                   Optional: written diagnoses for non-trivial fixes
  scripts/                   Operational scripts owned by this project:
                             launch wrappers (slurm/k8s), row counters,
                             coverage tallies, upload/publish, monitors,
                             offline replay/analysis harnesses
```

Created by `/design <name>` (or by hand from `templates/`). `scripts/` is the
ONLY sanctioned code location here; agents do not invent `src/` or other
folders.

## Where does code go? (the decision rule)

- **Infra repo**: anything the framework imports, anything that ships in a PR
  there - the generator itself, its prompts, seeded twins, unit tests.
- **`data_projects/<name>/scripts/`**: anything that orchestrates or observes
  RUNS of this project - launch scripts, batch processing/upload, monitoring,
  count/tally/analysis tools. These churn with the project lifecycle and
  would be noise in an infra PR.
- **Nowhere in synthloop**: generated DATA. Outputs stay in the infra's data
  dirs or your storage; this repo holds counts, verdicts, and pointers, never
  rows (size, and privacy if this repo is shared).

Scripts in `scripts/` typically run against the infra repo's environment;
invoke them through it (e.g. the infra's venv or `uv run --project <infra>`),
and record the exact incantations in the project runbook (`progress.md`) so
nobody guesses.

## Conventions

- The generator CODE lives in your own codebase, not here. This folder holds
  the process state and operational scripts around it.
- **One session, one project**: a working session scopes to a single
  generator unless it is explicitly a portfolio pass (`/status`). Parallel
  work on different generators belongs in parallel sessions; the per-project
  `progress.md` files are the coordination points, so sessions never need
  shared state beyond them.
- `progress.md` is append-only below the header; any agent or person resumes
  from its "Next action" line.
- Lessons that generalize beyond one generator get promoted from
  `project_memory.md` to `playbook/principles.md` in the same change, so
  every other in-flight generator inherits them immediately.
- `/status` gives the portfolio view: stages, next actions, blockers, and
  the queue of open questions awaiting the human.
