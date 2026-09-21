---
name: sl-cycle
description: Run the bounded synthloop smoke, review and repair loop through two clean passes or a hard stop.
---

# Synthloop Cycle

Read `CLAUDE.md` and `playbook/principles.md`, then follow the **cycle**
workflow in `playbook/workflows.md` and its referenced stage files. Resolve
these paths from the synthloop repository root, not the generator codebase.
Use `playbook/recovery.md` when resuming work or coordinating projects;
use `playbook/platforms.md` only for platform-specific execution or scheduling.

The project name and optional parameters come from the user's request. Resume
existing state and honor matching recorded authorization. Workflow rules and
pass criteria are defined in the shared playbook, not in this adapter.
