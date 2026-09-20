---
name: smoke
description: Run a synthloop functional smoke or validation batch with pinned provenance and full-batch checks.
---

# Synthloop Smoke

Read `CLAUDE.md` and `playbook/principles.md`, then follow the **smoke**
workflow in `playbook/workflows.md` and its referenced stage files. Resolve
these paths from the synthloop repository root, not the generator codebase.
Use `playbook/runtime.md` for state, evidence and shared executable checks;
use `playbook/platforms.md` only for platform-specific execution or scheduling.

The project name and optional parameters come from the user's request. Resume
existing state and honor matching recorded authorization. Workflow rules and
pass criteria are defined in the shared playbook, not in this adapter.
