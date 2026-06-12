---
name: status
description: Portfolio dashboard - show every generator in data_projects/ with its stage, next action, blockers, and latest batch verdict. Usage - /status [generator-name]
---

# /status [generator-name]

With a name: print that project's full `progress.md` header, latest batch
ledger row, latest review verdict, and open questions.

Without a name (portfolio view):

1. For every `data_projects/*/progress.md`, read the Current State header and
   the last batch ledger row.
2. Print one table:

   | Generator | Stage | Next action | Blocked on | Last batch (verdict) |

3. Below the table, list every project with open questions for the human,
   questions inline. These are the human's queue; surface them prominently.
4. Flag staleness: any project whose last session-ledger entry is old
   relative to the others, or whose next action has not changed across
   multiple sessions (a sign the loop is stuck or abandoned).

Read-only: this skill never modifies project files.
