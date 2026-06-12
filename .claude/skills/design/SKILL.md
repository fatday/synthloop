---
name: design
description: Start or resume the design stage for a data generator. Creates the project folder, interviews the user, and produces a design spec ready for the human gate. Usage - /design <generator-name>
---

# /design <generator-name>

1. If `data_projects/` itself does not exist yet, create it and copy
   `templates/data_projects_README.md` to `data_projects/README.md`; remind
   the user it is gitignored here and can be made its own PRIVATE repo
   (`git init` inside it) for team sharing. Then, if `data_projects/<name>/`
   does not exist, create it from `templates/`: `design_spec.md`,
   `progress.md`, `project_memory.md`, and `review_instructions/v1.md`
   (from `templates/review_instruction.md`). Set progress stage to
   `1-design`.
2. Read `data_projects/ENVIRONMENT.md` (if missing, instantiate it from
   `templates/environment.md`: first run `/survey` to detect and classify
   the workspace directories, then fill the rest by reading the detected
   data-infra repo and interviewing the user about goals and conventions -
   this pays off for every future generator). Then read `playbook/00_context.md` and
   `playbook/01_design.md` in full. Execute stage 0 first if the Context
   section is empty: pull the target format, reference generators, and
   benchmark style from the environment file, and read the nearest existing
   generator BEFORE asking the user questions you could answer yourself.
3. Interview the user only for what code and data cannot tell you: goals,
   non-goals, taste, constraints, risk tolerances. Batch the questions.
4. Fill every section of the design spec. The Behavior Coverage Spec needs
   numbers; the External Reality Checks need all four answers. Where you
   propose a default, mark it `(proposed)` so the human can veto cheaply.
5. Collect open questions into section 9 and into `progress.md`.
6. Present to the human: a short summary, the open questions, and where the
   full spec lives. STOP. Do not proceed to implementation without explicit
   approval. Record the approval in `progress.md` under Gates.
