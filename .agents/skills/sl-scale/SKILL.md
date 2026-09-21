---
name: sl-scale
description: Prepare and execute a synthloop scale plan only with matching explicit human authorization.
---

# Synthloop Scale

Read `CLAUDE.md` and `playbook/principles.md`, then follow the **scale**
workflow in `playbook/workflows.md` and its referenced stage files. Resolve
these paths from the synthloop repository root, not the generator codebase.
Use `playbook/recovery.md` when resuming work or coordinating projects;
use `playbook/platforms.md` only for platform-specific execution or scheduling.

The project name and optional parameters come from the user's request. Resume
existing state and honor matching recorded authorization. Workflow rules and
pass criteria are defined in the shared playbook, not in this adapter.
