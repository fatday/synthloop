---
name: sl-design
description: Start or resume synthloop generator design. Use when asked to design a data generator, create a data_projects project folder, run stage 0/1, or run the Claude design workflow.
---

# Synthloop Design

Create or resume a generator project and stop at the human design gate.

1. Read `CLAUDE.md`, `playbook/principles.md`, `playbook/00_context.md`, and
   `playbook/01_design.md`.
2. Ensure `data_projects/` exists. If not, create it and copy
   `templates/data_projects_README.md` to `data_projects/README.md`.
3. Ensure `data_projects/ENVIRONMENT.md` exists. If missing, run the
   `sl-survey` workflow first, then fill the remaining environment fields
   by reading the data-infra repo and asking only questions code cannot answer.
4. If `data_projects/<name>/` is missing, instantiate it from templates:
   `design_spec.md`, `progress.md`, `project_memory.md`, and
   `review_instructions/v1.md` from `templates/review_instruction.md`.
5. Read any existing project `progress.md` and `project_memory.md` before
   continuing.
6. Fill the design spec with concrete coverage numbers, reality checks, goals,
   non-goals, and open questions. Mark proposed defaults as `(proposed)`.
7. Update `progress.md` with the current stage, open questions, and one next
   action.
8. Present a concise spec summary and stop. Do not implement until the human
   explicitly approves the design gate.
