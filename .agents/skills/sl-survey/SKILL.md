---
name: sl-survey
description: Run synthloop's workspace survey. Use when asked to classify accessible directories, bootstrap or refresh data_projects/ENVIRONMENT.md, find the data-infra repo, or run the `/survey` Claude-equivalent workflow.
---

# Synthloop Survey

Classify the workspace roots and update shared environment context.

1. Read `CLAUDE.md`, `playbook/principles.md`, and `playbook/survey.md`.
2. If `data_projects/` is missing, create it and copy
   `templates/data_projects_README.md` to `data_projects/README.md`.
3. If `data_projects/ENVIRONMENT.md` is missing, instantiate it from
   `templates/environment.md`.
4. Inspect each accessible root by reading its README, project config, and
   top-level structure. Classify by evidence, not directory names.
5. Record path, role, deciding evidence, intended use, and confirmation status
   in `data_projects/ENVIRONMENT.md`.
6. Preserve human-confirmed rows; propose changes to them instead of silently
   rewriting them.
7. Stop if no accessible directory classifies as `data-infra`; ask the human to
   grant or identify the generator codebase before design/implementation work.

End by reporting the table and any unknown or low-confidence rows.
