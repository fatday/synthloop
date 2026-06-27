---
name: sl-status
description: Show synthloop project or portfolio status. Use when asked for synthloop status, a generator progress dashboard, open human questions, blockers, stale projects, or the `/status` Claude-equivalent workflow.
---

# Synthloop Status

Run the read-only portfolio status workflow.

1. Read `CLAUDE.md`, then `playbook/principles.md`.
2. Read `data_projects/ENVIRONMENT.md` if it exists.
3. If the user named a generator, read `data_projects/<name>/progress.md`,
   `project_memory.md`, and the latest review summary if referenced.
4. If no generator is named, read every `data_projects/*/progress.md`.
5. Print the portfolio table:

   | Generator | Stage | Next action | Blocked on | Last batch verdict |

6. List open human questions prominently.
7. Flag stale projects whose next action has not changed across sessions, or
   whose latest ledger entry is old relative to the others.

Do not modify files.
